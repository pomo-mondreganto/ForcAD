from typing import List

import storage
from helplib import models
from helplib.cache import cache_helper, async_cache_helper
from helplib.types import TaskStatus, Action
from storage import caching

_SELECT_TEAMTASKS_QUERY = "SELECT * from teamtasks"


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


async def tasks_async_getter(redis_aio, pipe):
    """Get list of tasks registered in the database (asynchronous version)"""
    await async_cache_helper(
        redis_aio=redis_aio,
        cache_key='tasks:cached',
        cache_func=caching.cache_tasks,
    )
    pipe.smembers('tasks')


def update_task_status(task_id: int, team_id: int, round: int, checker_verdict: models.CheckerVerdict):
    """ Update task status in database

        :param task_id:
        :param team_id:
        :param round:
        :param checker_verdict: instance of CheckerActionResult
    """
    add = 0
    public = checker_verdict.public_message
    if checker_verdict.status == TaskStatus.UP:
        add = 1
        if checker_verdict.action == Action.PUT:
            public = 'OK'

    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.callproc(
            'update_teamtasks_status',
            (
                round,
                team_id,
                task_id,
                checker_verdict.status.value,
                add,
                public,
                checker_verdict.private_message,
                checker_verdict.command,
            )
        )
        data = curs.fetchone()
        conn.commit()

    data['round'] = round
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.xadd(f'teamtasks:{team_id}:{task_id}', dict(data), maxlen=50, approximate=False).execute()


def get_last_teamtasks() -> List[dict]:
    """Fetch team tasks, last for each team for each task
        :return: dictionary of team tasks or None
    """
    teams = storage.teams.get_teams()
    tasks = storage.tasks.get_tasks()

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        for team in teams:
            for task in tasks:
                pipeline.xrevrange(f'teamtasks:{team.id}:{task.id}', count=1)
        data = pipeline.execute()

    data = sum(data, [])

    results = []
    for timestamp, record in data:
        record['timestamp'] = timestamp
        results.append(record)

    process_teamtasks(results)

    return results


def get_teamtasks_from_db() -> List[dict]:
    """Fetch current team tasks from database
        :return: dictionary of team tasks or None
    """
    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(_SELECT_TEAMTASKS_QUERY)
        data = curs.fetchall()

    return data


async def get_teamtasks_of_team_async(team_id: int, loop) -> List[dict]:
    """Fetch teamtasks for team for all tasks"""
    redis_aio = await storage.get_async_redis_storage(loop)
    pipe = redis_aio.pipeline()
    await storage.tasks.tasks_async_getter(redis_aio, pipe)
    tasks, = await pipe.execute()
    tasks = [models.Task.from_json(task) for task in tasks]

    tr = redis_aio.multi_exec()

    for task in tasks:
        tr.xrevrange(f'teamtasks:{team_id}:{task.id}')

    data = await tr.execute()
    data = sum(data, [])

    results = []
    for timestamp, record in data:
        record['timestamp'] = timestamp
        results.append(record)

    return results


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


def process_teamtasks(teamtasks: List[dict]):
    casts = (
        (['id', 'team_id', 'task_id', 'checks', 'checks_passed', 'round'], int),
        (['score'], float),
    )
    for each in teamtasks:
        for keys, t in casts:
            for key in keys:
                each[key] = t(each[key])
