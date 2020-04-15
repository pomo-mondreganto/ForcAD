from typing import List, Optional

import storage
from helplib import models
from helplib.cache import cache_helper, async_cache_helper
from storage import caching

TEAM_INSERT_QUERY = '''
INSERT INTO Teams 
(name, ip, token, highlighted) 
VALUES (%(name)s, %(ip)s, %(token)s, %(highlighted)s) 
RETURNING id
'''

TEAM_UPDATE_QUERY = '''
UPDATE Teams 
SET name = %(name)s, ip = %(ip)s, token = %(token)s, highlighted = %(highlighted)s
WHERE id = %(id)s
'''

TEAM_DELETE_QUERY = 'DELETE FROM Teams WHERE id = %s'


def get_teams() -> List[models.Team]:
    """Get list of teams registered in the database"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cache_helper(
            pipeline=pipeline,
            cache_key='teams:cached',
            cache_func=caching.cache_teams,
            cache_args=(pipeline,),
        )

        teams, = pipeline.smembers('teams').execute()
        teams = list(models.Team.from_json(team) for team in teams)

    return teams


async def teams_async_getter(redis_aio, pipe):
    """Get list of teams registered in the database (asynchronous version)"""
    await async_cache_helper(
        redis_aio=redis_aio,
        cache_key='teams:cached',
        cache_func=caching.cache_teams,
    )
    pipe.smembers('teams')


def get_team_id_by_token(token: str) -> Optional[int]:
    """Get team by token

        :param token: token string
        :return: team id
    """

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cache_helper(
            pipeline=pipeline,
            cache_key='teams:cached',
            cache_func=caching.cache_teams,
            cache_args=(pipeline,),
        )
        team_id, = pipeline.get(f'team:token:{token}').execute()

    try:
        team_id = int(team_id)
    except (ValueError, TypeError):
        return None
    else:
        return team_id


async def create_team(team: models.Team):
    async with storage.async_db_cursor() as (_conn, curs):
        await curs.execute(TEAM_INSERT_QUERY, team.to_dict())
        result, = await curs.fetchone()
        team.id = result

        redis_aio = await storage.get_async_redis_storage()
        pipe = redis_aio.pipeline()
        pipe.delete("teams", "teams:cached")
        await storage.tasks.tasks_async_getter(redis_aio, pipe)
        _, tasks = await pipe.execute()
        tasks = [models.Task.from_json(task) for task in tasks]

        insert_data = [
            (task.id, team.id, task.default_score, -1)
            for task in tasks
        ]

        for each in insert_data:
            await curs.execute(storage.tasks.TEAMTASK_INSERT_QUERY, each)

    return team


async def update_team(team: models.Team):
    async with storage.async_db_cursor() as (_conn, curs):
        await curs.execute(TEAM_UPDATE_QUERY, team.to_dict())

    redis_aio = await storage.get_async_redis_storage()
    pipe = redis_aio.pipeline()
    pipe.delete("teams", "teams:cached")
    await pipe.execute()

    return team


async def delete_team(team_id: int):
    async with storage.async_db_cursor() as (_conn, curs):
        await curs.execute(TEAM_DELETE_QUERY, (team_id,))

        redis_aio = await storage.get_async_redis_storage()
        pipe = redis_aio.pipeline()
        pipe.delete("teams", "teams:cached")
        await storage.tasks.tasks_async_getter(redis_aio, pipe)
        _, tasks = await pipe.execute()
        tasks = [models.Task.from_json(task) for task in tasks]

        delete_data = [
            (task.id, team_id)
            for task in tasks
        ]

        for each in delete_data:
            await curs.execute(storage.tasks.TEAMTASK_DELETE_QUERY, each)
