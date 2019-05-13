import json
from typing import List, Optional

import aioredis
import redis

import storage
from helpers import models, rating
from storage import caching

_SELECT_SCORE_BY_TEAM_TASK_QUERY = "SELECT score from teamtasks WHERE team_id=%s AND task_id=%s AND round=%s"

_UPDATE_TEAMTASKS_SCORE_QUERY = "UPDATE teamtasks SET score = %s WHERE team_id=%s AND task_id=%s AND round=%s"


def get_teams() -> List[models.Team]:
    """Get list of teams registered in the database"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        while True:
            try:
                pipeline.watch('teams:cached')

                cached = pipeline.exists('teams:cached')
                if not cached:
                    caching.cache_teams()

                break
            except redis.WatchError:
                continue

        # pipeline is not in multi mode now
        teams = pipeline.smembers('teams')
        teams = list(models.Team.from_json(team) for team in teams)

    return teams


async def get_teams_async(loop) -> List[models.Team]:
    """Get list of teams registered in the database (asynchronous version)"""

    redis_aio = await storage.get_async_redis_pool(loop)

    while True:
        try:
            await redis_aio.watch('teams:cached')

            cached = await redis_aio.exists('teams:cached')
            if not cached:
                # TODO: make it asynchronous?
                caching.cache_teams()

            await redis_aio.unwatch()
        except aioredis.WatchVariableError:
            continue
        else:
            break

    teams = await redis_aio.smembers('teams')
    teams = list(models.Team.from_json(team) for team in teams)

    return teams


def get_team_id_by_token(token: str) -> Optional[int]:
    """Get team by token

        :param token: token string
        :return: team id
    """
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        while True:
            try:
                pipeline.watch('teams:cached')

                cached = pipeline.exists('teams:cached')
                if not cached:
                    caching.cache_teams()

                break
            except redis.WatchError:
                continue

        # pipeline is not in multi mode now
        team_id = pipeline.get(f'team:token:{token}')

    try:
        team_id = int(team_id.decode())
    except (ValueError, AttributeError):
        return None
    else:
        return team_id


def handle_attack(attacker_id: int, victim_id: int, task_id: int, round: int) -> float:
    """Recalculate team ratings and publish redis message

        :param attacker_id: id of the attacking team
        :param victim_id: id of the victim team
        :param task_id: id of task which is attacked
        :param round: round of the attack
    """

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    curs.execute(_SELECT_SCORE_BY_TEAM_TASK_QUERY, (attacker_id, task_id, round))
    attacker_score, = curs.fetchone()

    curs.execute(_SELECT_SCORE_BY_TEAM_TASK_QUERY, (victim_id, task_id, round))
    victim_score, = curs.fetchone()

    rs = rating.RatingSystem(attacker=attacker_score, victim=victim_score)
    attacker_delta, victim_delta = rs.calculate()

    curs.execute(_UPDATE_TEAMTASKS_SCORE_QUERY, (attacker_score + attacker_delta, attacker_id, task_id, round))
    curs.execute(_UPDATE_TEAMTASKS_SCORE_QUERY, (victim_score + victim_delta, victim_id, task_id, round))

    conn.commit()
    curs.close()
    storage.get_db_pool().putconn(conn)

    flag_data = {
        'attacker_id': attacker_id,
        'victim_id': victim_id,
        'attacker_delta': attacker_delta,
        'victim_delta': victim_delta,
    }

    with storage.get_redis_storage().pipeline() as pipeline:
        pipeline.publish('stolen_flags', json.dumps(flag_data))

    return attacker_delta
