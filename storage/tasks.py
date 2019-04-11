import json
from typing import List

import helpers.status
import storage
from helpers import models
from storage import caching


def get_tasks() -> List[models.Task]:
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('tasks:cached').execute()
        if not cached:
            caching.cache_tasks()

        tasks, = pipeline.smembers('tasks').execute()
        tasks = list(models.Task.from_json(task) for task in tasks)

    return tasks


def update_task_status(task_id: int, team_id: int, status: helpers.status.TaskStatus, message: str):
    query = "UPDATE teamtasks SET status = %s, message = %s WHERE task_id = %s AND team_id = %s"
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()
    curs.execute(query, (status.value, message, task_id, team_id))
    conn.commit()
    storage.get_db_pool().putconn(conn)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.set(f'team_{team_id}:task_{task_id}:cached', 1)
        pipeline.set(f'team_{team_id}:task_{task_id}:status', status.value)
        pipeline.set(f'team_{team_id}:task_{task_id}:message', message)
        pipeline.execute()


def get_teamtasks(round: int):
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        result, = pipeline.get(f'teamtasks:{round}').execute()
        if not result:
            return None
        return json.loads(result.decode())
