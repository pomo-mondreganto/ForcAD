from typing import List

from lib import models, storage
from lib.helpers.cache import cache_helper
from lib.models import TaskStatus, Action
from lib.storage import caching
from lib.storage.keys import CacheKeys

_SELECT_TEAMTASKS_QUERY = "SELECT * from TeamTasks"

TEAMTASK_INSERT_QUERY = '''
INSERT INTO TeamTasks
(task_id, team_id, score, status)
VALUES (%(task_id)s, %(team_id)s, %(score)s, %(status)s)
'''

# noinspection SqlInsertValues
_SELECT_TEAMTASK_LOG_QUERY = '''
WITH logged_teamtasks AS (
    SELECT * FROM TeamTasksLog
    WHERE team_id=%(team_id)s AND task_id=%(task_id)s
)
SELECT (SELECT MAX(id) FROM logged_teamtasks) + 1 AS id,
       (SELECT real_round FROM GameConfig WHERE id=1) AS round,
       *,
       now() AS ts
FROM TeamTasks
WHERE team_id=%(team_id)s AND task_id=%(task_id)s
UNION SELECT * FROM logged_teamtasks
ORDER BY id DESC
'''

_INSERT_TEAMTASKS_TO_LOG_QUERY = '''
INSERT INTO TeamTasksLog
(round, task_id, team_id, status, stolen, lost, score, checks, checks_passed,
public_message, private_message, command)
SELECT %(round)s, %(task_id)s, %(team_id)s, status, stolen, lost, score,
    checks, checks_passed, public_message, private_message, command
FROM TeamTasks
WHERE
team_id = %(team_id)s AND task_id = %(task_id)s
FOR NO KEY UPDATE
'''

_UPDATE_TEAMTASKS_QUERY = '''
UPDATE TeamTasks
SET status = %(status)s,
    public_message = %(public_message)s,
    private_message = %(private_message)s,
    command = %(command)s,
    checks_passed = checks_passed + %(passed)s,
    checks = checks + 1
WHERE
team_id = %(team_id)s AND task_id = %(task_id)s
RETURNING *
'''


def get_tasks() -> List[models.Task]:
    """Get list of tasks registered in database."""
    key = CacheKeys.tasks()
    with storage.utils.redis_pipeline(transaction=True) as pipe:
        cache_helper(
            pipeline=pipe,
            cache_key=key,
            cache_func=caching.cache_tasks,
            cache_args=(pipe,),
        )

        tasks, = pipe.smembers(key).execute()
        tasks = list(models.Task.from_json(task) for task in tasks)

    return tasks


def get_all_tasks() -> List[models.Task]:
    """Get list of all tasks, including inactive."""
    with storage.utils.db_cursor(dict_cursor=True) as (_, curs):
        curs.execute(models.Task.get_select_all_query())
        tasks = curs.fetchall()

    tasks = list(models.Task.from_dict(task) for task in tasks)
    return tasks


def update_task_status(
        task_id: int,
        team_id: int,
        current_round: int,
        checker_verdict: models.CheckerVerdict,
) -> None:
    """
    Update task status in database.

    :param task_id:
    :param team_id:
    :param current_round:
    :param checker_verdict: instance of CheckerActionResult
    """
    add = 0
    public = checker_verdict.public_message
    if checker_verdict.status == TaskStatus.UP:
        add = 1
        if checker_verdict.action == Action.PUT:
            public = 'OK'

    params = {
        'round': current_round,
        'task_id': task_id,
        'team_id': team_id,
        'status': checker_verdict.status.value,
        'public_message': public,
        'private_message': checker_verdict.private_message,
        'command': checker_verdict.command,
        'passed': add,
    }

    with storage.utils.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(_INSERT_TEAMTASKS_TO_LOG_QUERY, params)
        curs.execute(_UPDATE_TEAMTASKS_QUERY, params)
        data = curs.fetchone()
        conn.commit()

    data['round'] = current_round
    with storage.utils.redis_pipeline(transaction=True) as pipe:
        pipe.xadd(
            CacheKeys.teamtasks(team_id, task_id),
            dict(data),
            maxlen=50,
            approximate=False,
        ).execute()


def get_last_teamtasks() -> List[dict]:
    """Fetch team tasks, last for each team for each task."""
    teams = storage.teams.get_teams()
    tasks = storage.tasks.get_tasks()

    with storage.utils.redis_pipeline(transaction=True) as pipe:
        for team in teams:
            for task in tasks:
                pipe.xrevrange(CacheKeys.teamtasks(team.id, task.id), count=1)
        data = pipe.execute()

    data = sum(data, [])

    results = []
    for timestamp, record in data:
        record['timestamp'] = timestamp
        results.append(record)

    results = process_teamtasks(results)

    return results


def get_teamtasks_from_db() -> List[dict]:
    """
    Fetch current team tasks from database.

    :returns: dictionary of team tasks or None
    """
    with storage.utils.db_cursor(dict_cursor=True) as (_, curs):
        curs.execute(_SELECT_TEAMTASKS_QUERY)
        data = curs.fetchall()

    return data


def get_teamtasks_for_team(team_id: int) -> List[dict]:
    """Fetch teamtasks for team for all tasks."""

    tasks = storage.tasks.get_tasks()

    with storage.utils.redis_pipeline(transaction=False) as pipe:
        for task in tasks:
            pipe.xrevrange(CacheKeys.teamtasks(team_id, task.id))
        data = pipe.execute()

    data = sum(data, [])

    results = []
    for timestamp, record in data:
        record['timestamp'] = timestamp
        results.append(record)

    return results


def filter_teamtasks_for_participants(teamtasks: List[dict]) -> List[dict]:
    """
    Filter sensitive data from teamtasks.

    Remove private message and rename public message
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


def process_teamtasks(teamtasks: List[dict]) -> List[dict]:
    """
    Force correct types on teamtasks list.

    :returns: processed list
    """
    casts = (
        (
            ['team_id', 'task_id', 'checks', 'checks_passed', 'round'],
            int,
        ),
        (
            ['score'],
            float,
        ),
    )
    for each in teamtasks:
        for keys, t in casts:
            for key in keys:
                each[key] = t(each[key])

    return teamtasks


def create_task(task: models.Task) -> models.Task:
    """Add new task to DB, reset cache & return created instance."""
    with storage.utils.db_cursor() as (conn, curs):
        task.insert(curs)

        insert_data = (
            {
                'task_id': task.id,
                'team_id': team.id,
                'score': task.default_score,
                'status': -1,
            }
            for team in storage.teams.get_all_teams()
        )
        curs.executemany(TEAMTASK_INSERT_QUERY, insert_data)

        conn.commit()

    storage.caching.flush_tasks_cache()
    return task


def update_task(task: models.Task) -> models.Task:
    """Update task, reset cache & return updated instance."""
    with storage.utils.db_cursor() as (conn, curs):
        curs.execute(task.get_update_query(), task.to_dict())
        conn.commit()

    storage.caching.flush_tasks_cache()
    return task


def delete_task(task_id: int) -> None:
    """Set active = False on a task."""
    with storage.utils.db_cursor() as (conn, curs):
        curs.execute(models.Task.get_delete_query(), {'id': task_id})
        conn.commit()

    storage.caching.flush_tasks_cache()


def get_admin_teamtask_history(team_id: int, task_id: int) -> List[dict]:
    """Get teamtasks from log table by team & task ids pair."""
    with storage.utils.db_cursor(dict_cursor=True) as (_, curs):
        curs.execute(
            _SELECT_TEAMTASK_LOG_QUERY,
            {
                'team_id': team_id,
                'task_id': task_id,
            },
        )
        results = curs.fetchall()

    for each in results:
        each['ts'] = each['ts'].timestamp()

    return results
