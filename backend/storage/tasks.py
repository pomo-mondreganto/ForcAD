import json
from typing import List

import redis

import helpers
import storage
from helpers import models
from storage import caching

_UPDATE_TEAMTASKS_STATUS_QUERY = f"""
UPDATE teamtasks SET status = %s, message = %s, up_rounds = up_rounds + %s
WHERE task_id = %s AND team_id = %s AND round = %s
"""

_INITIALIZE_TEAMTASKS_FROM_PREVIOUS_QUERY = """
WITH prev_table AS (
    SELECT score, stolen, lost, up_rounds FROM teamtasks 
    WHERE task_id = %(task_id)s AND team_id = %(team_id)s AND round = %(round)s - 1
)
INSERT INTO TeamTasks (task_id, team_id, round, score, stolen, lost, up_rounds) 
SELECT %(task_id)s, %(team_id)s, %(round)s, score, stolen, lost, up_rounds 
FROM prev_table
"""


def get_tasks() -> List[models.Task]:
    """Get list of tasks registered in database"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        while True:
            try:
                pipeline.watch('tasks:cached')
                cached = pipeline.exists('tasks:cached')
                if not cached:
                    caching.cache_tasks()

                break
            except redis.WatchError:
                continue

        # pipeline is not in multi mode now
        tasks = pipeline.smembers('tasks')
        tasks = list(models.Task.from_json(task) for task in tasks)

    return tasks


async def get_tasks_async(loop) -> List[models.Task]:
    """Get list of tasks registered in the database (asynchronous version)"""

    # FIXME: possible race condition, add lock on teams:cached
    redis_aio = await storage.get_async_redis_pool(loop)
    cached = await redis_aio.exists('tasks:cached')
    if not cached:
        # TODO: make it asynchronous?
        caching.cache_tasks()

    tasks = await redis_aio.smembers('tasks')
    tasks = list(models.Task.from_json(task) for task in tasks)

    return tasks


def update_task_status(task_id: int, team_id: int, round: int, status: helpers.status.TaskStatus, message: str):
    """ Update task status in database

        :param task_id: task id
        :param team_id: team id
        :param round: round to update table for
        :param status: TaskStatus instance
        :param message: custom message to show in scoreboard
    """
    add = 0
    if status == helpers.status.TaskStatus.UP:
        add = 1

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()
    curs.execute(
        _UPDATE_TEAMTASKS_STATUS_QUERY,
        (
            status.value,
            message,
            add,
            task_id,
            team_id,
            round,
        )
    )

    conn.commit()
    curs.close()
    storage.get_db_pool().putconn(conn)


def get_teamtasks(round: int):
    """Fetch team tasks for current specified round

        :param round: current round
        :return: dictionary of team tasks or None
    """
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.get(f'teamtasks:{round}:cached')
        pipeline.get(f'teamtasks:{round}')
        cached, result = pipeline.execute()

        if not cached:
            return None
        return json.loads(result.decode())


def initialize_teamtasks(round: int):
    """Add blank entries to "teamtasks" table for a new round

        :param round: round to create entries for
    """

    teams = storage.teams.get_teams()
    tasks = storage.tasks.get_tasks()

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    for team in teams:
        for task in tasks:
            curs.execute(
                _INITIALIZE_TEAMTASKS_FROM_PREVIOUS_QUERY,
                {
                    'task_id': task.id,
                    'team_id': team.id,
                    'round': round,
                },
            )

    conn.commit()
    curs.close()
    storage.get_db_pool().putconn(conn)
