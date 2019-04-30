import json
from typing import List

import helpers.status
import storage
from helpers import models
from storage import caching


def get_tasks() -> List[models.Task]:
    """Get list of tasks registered in database"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('tasks:cached').execute()
        if not cached:
            caching.cache_tasks()

        tasks, = pipeline.smembers('tasks').execute()
        tasks = list(models.Task.from_json(task) for task in tasks)

    return tasks


async def get_tasks_async(loop) -> List[models.Task]:
    """Get list of tasks registered in the database (asynchronous version)"""
    redis = await storage.get_async_redis_pool(loop)
    cached = await redis.exists('tasks:cached')
    if not cached:
        # TODO: make it asynchronous?
        caching.cache_tasks()

    tasks = await redis.smembers('tasks')
    tasks = list(models.Task.from_json(task) for task in tasks)

    return tasks


def update_task_status(task_id: int, team_id: int, status: helpers.status.TaskStatus, message: str):
    """ Update task status in database

        :param task_id: task id
        :param team_id: team id
        :param status: TaskStatus instance
        :param message: custom message to show in scoreboard
    """
    add = 0
    if status == helpers.status.TaskStatus.UP:
        add = 1

    query = (
        f"UPDATE teamtasks SET status = %s, message = %s, up_rounds = up_rounds + %s "
        "WHERE task_id = %s AND team_id = %s"
    )

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()
    curs.execute(
        query,
        (
            status.value,
            message,
            add,
            task_id,
            team_id,
        )
    )

    conn.commit()
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
