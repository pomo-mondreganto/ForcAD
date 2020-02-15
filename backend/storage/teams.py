from kombu.utils import json
from typing import List, Optional

import storage
from helplib import models, flags
from helplib.cache import cache_helper, async_cache_helper
from storage import caching


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


async def get_teams_async(loop) -> List[models.Team]:
    """Get list of teams registered in the database (asynchronous version)"""

    redis_aio = await storage.get_async_redis_storage(loop)

    await async_cache_helper(
        redis_aio=redis_aio,
        cache_key='teams:cached',
        cache_func=caching.cache_teams_async,
    )

    teams = await redis_aio.smembers('teams')
    teams = list(models.Team.from_json(team) for team in teams)

    return teams


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
        team_id = int(team_id.decode())
    except (ValueError, AttributeError):
        return None
    else:
        return team_id


def handle_attack(attacker_id: int, flag_str: str, round: int) -> float:
    """Check flag, lock team for update, call rating recalculation,
        then publish redis message about stolen flag

        :param attacker_id: id of the attacking team
        :param flag_str: flag to be checked
        :param round: round of the attack

        :raises FlagSubmitException: when flag check was failed
        :return: attacker rating change
    """

    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        flag = flags.try_add_stolen_flag_by_str(flag_str=flag_str, attacker=attacker_id, round=round)

        with storage.db_cursor() as (conn, curs):
            curs.callproc("recalculate_rating", (attacker_id, flag.team_id, flag.task_id, flag.id))
            attacker_delta, victim_delta = curs.fetchone()
            conn.commit()

        flag_data = {
            'attacker_id': attacker_id,
            'victim_id': flag.team_id,
            'task_id': flag.task_id,
            'attacker_delta': attacker_delta,
            'victim_delta': victim_delta,
        }

        pipeline.publish('stolen_flags', json.dumps(flag_data)).execute()

    return attacker_delta
