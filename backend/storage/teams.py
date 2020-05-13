from typing import List, Optional

import storage
from helplib import models
from helplib.cache import cache_helper, async_cache_helper
from storage import caching


def get_teams() -> List[models.Team]:
    """Get list of teams registered in the database."""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cache_helper(
            pipeline=pipeline,
            cache_key='teams',
            cache_func=caching.cache_teams,
            cache_args=(pipeline,),
        )

        teams, = pipeline.smembers('teams').execute()
        teams = list(models.Team.from_json(team) for team in teams)

    return teams


async def teams_async_getter(redis_aio, pipe) -> None:  # type: ignore
    """Cache teams if not cached, then add fetch command to pipe."""
    await async_cache_helper(
        redis_aio=redis_aio,
        cache_key='teams',
        cache_func=caching.cache_teams,
    )
    pipe.smembers('teams')


async def get_all_teams_async() -> List[models.Team]:
    """Get list of all teams from database."""
    async with storage.async_db_cursor(dict_cursor=True) as (_conn, curs):
        await curs.execute(models.Team.get_select_all_query())
        results = await curs.fetchall()

    teams = [models.Team.from_dict(team) for team in results]
    return teams


def get_team_id_by_token(token: str) -> Optional[int]:
    """
    Get team by token.

    :param token: token string
    :return: team id
    """
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        team_id, = pipeline.get(f'team:token:{token}').execute()

    try:
        team_id = int(team_id)
    except (ValueError, TypeError):
        return None
    else:
        return team_id


async def create_team(team: models.Team) -> models.Team:
    """Add new team to DB, reset cache & return created instance."""
    async with storage.async_db_cursor() as (_conn, curs):
        await curs.execute(team.get_insert_query(), team.to_dict())
        result, = await curs.fetchone()
        team.id = result

        tasks = await storage.tasks.get_all_tasks_async()
        insert_data = [
            (task.id, team.id, task.default_score, -1)
            for task in tasks
        ]

        for each in insert_data:
            await curs.execute(storage.tasks.TEAMTASK_INSERT_QUERY, each)

    redis_aio = await storage.get_async_redis_storage()
    await redis_aio.delete('teams')

    return team


async def update_team(team: models.Team) -> models.Team:
    """Update team, reset cache & return updated instance."""
    async with storage.async_db_cursor() as (_conn, curs):
        await curs.execute(team.get_update_query(), team.to_dict())

    redis_aio = await storage.get_async_redis_storage()
    await redis_aio.delete('teams')

    return team


async def delete_team(team_id: int) -> None:
    """Set active = False on a team."""
    async with storage.async_db_cursor() as (_conn, curs):
        await curs.execute(models.Team.get_delete_query(), {'id': team_id})

    redis_aio = await storage.get_async_redis_storage()
    await redis_aio.delete('teams')
