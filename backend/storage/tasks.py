from kombu.utils import json
from typing import List, Optional

import storage
from helplib import models
from helplib.cache import cache_helper, async_cache_helper
from helplib.status import TaskStatus
from storage import caching

_UPDATE_TEAMTASKS_STATUS_QUERY = """
UPDATE teamtasks SET status = %s, public_message = %s, private_message = %s, command = %s, 
checks_passed = checks_passed + %s, checks = checks + 1
WHERE task_id = %s AND team_id = %s AND round >= %s
RETURNING *
"""

_INITIALIZE_TEAMTASKS_FROM_PREVIOUS_QUERY = """
INSERT INTO TeamTasks (task_id, team_id, round, score, stolen, lost, checks_passed, checks) 
SELECT %(task_id)s, %(team_id)s, %(round)s, score, stolen, lost, checks_passed, checks 
FROM teamtasks 
WHERE task_id = %(task_id)s AND team_id = %(team_id)s AND round <= %(round)s - 1
ORDER BY round DESC LIMIT 1 FOR NO KEY UPDATE;
"""

_SELECT_TEAMTASKS_BY_ROUND_QUERY = "SELECT * from teamtasks WHERE round = %s ORDER BY id"


def get_tasks() -> List[models.Task]:
    """Get list of tasks registered in database"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cache_helper(
            pipeline=pipeline,
            cache_key='tasks:cached',
            cache_func=caching.cache_tasks,
            cache_args=(pipeline,),
        )

        tasks, = pipeline.smembers('tasks').execute()
        tasks = list(models.Task.from_json(task) for task in tasks)

    return tasks


async def get_tasks_async(loop) -> List[models.Task]:
    """Get list of tasks registered in the database (asynchronous version)"""

    redis_aio = await storage.get_async_redis_storage(loop)

    await async_cache_helper(
        redis_aio=redis_aio,
        cache_key='tasks:cached',
        cache_func=caching.cache_tasks_async,
    )

    tasks = await redis_aio.smembers('tasks')
    tasks = list(models.Task.from_json(task) for task in tasks)

    return tasks


def update_task_status(task_id: int, team_id: int, round: int, checker_verdict: models.CheckerVerdict):
    """ Update task status in database

        :param task_id: task id
        :param team_id: team id
        :param round: round to update table for
        :param checker_verdict: instance of CheckerActionResult
    """
    add = 0
    public = checker_verdict.public_message
    if checker_verdict.status == TaskStatus.UP:
        add = 1
        if checker_verdict.action.upper() == 'PUT':
            public = 'OK'

    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(
            _UPDATE_TEAMTASKS_STATUS_QUERY,
            (
                checker_verdict.status.value,
                public,
                checker_verdict.private_message,
                checker_verdict.command,
                add,
                task_id,
                team_id,
                round,
            )
        )
        data = curs.fetchone()
        conn.commit()

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.xadd(f'teamtasks:{team_id}:{task_id}', dict(data), maxlen=20, approximate=False)
        pipeline.execute()


def get_teamtasks(round: int) -> Optional[List[dict]]:
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

    teamtasks = json.loads(result)
    return teamtasks


def filter_teamtasks_for_participants(teamtasks: List[dict]) -> List[dict]:
    """Remove private message and rename public message
    to "message" for a list of teamtasks, remove 'command'
    """
    result = []

    for obj in teamtasks:
        obj['message'] = obj['public_message']
        obj.pop('private_message')
        obj.pop('public_message')
        obj.pop('command')
        result.append(obj)

    return result


def get_teamtasks_for_participants(round: int) -> Optional[List[dict]]:
    """Fetch team tasks for current specified round, with private message removed

        :param round: current round
        :return: dictionary of team tasks or None
    """
    return filter_teamtasks_for_participants(get_teamtasks(round=round))


def get_teamtasks_of_team(team_id: int) -> Optional[List[dict]]:
    """Fetch teamtasks for team for each task"""
    tasks = get_tasks()
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        for task in tasks:
            pipeline.xrange(f'teamtasks:{team_id}:{task.id}')

        data = pipeline.execute()

    data = sum(data, [])
    results = []
    for timestamp, record in data:
        record['timestamp'] = timestamp
        results.append(record)

    return results


def get_teamtasks_of_team_for_participants(team_id: int) -> Optional[List[dict]]:
    """Fetch teamtasks history for a team, cache if necessary, with private message stripped"""
    return filter_teamtasks_for_participants(
        get_teamtasks_of_team(
            team_id=team_id,
        )
    )


def initialize_teamtasks(round: int):
    """Add blank entries to "teamtasks" table for a new round

        :param round: round to create entries for
    """

    teams = storage.teams.get_teams()
    tasks = storage.tasks.get_tasks()

    with storage.db_cursor() as (conn, curs):
        data = [
            {
                'task_id': task.id,
                'team_id': team.id,
                'round': round,
            }
            for team in teams
            for task in tasks
        ]

        curs.executemany(
            _INITIALIZE_TEAMTASKS_FROM_PREVIOUS_QUERY,
            data,
        )
        conn.commit()
