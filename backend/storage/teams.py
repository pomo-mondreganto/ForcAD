import json
from typing import List, Optional, Tuple

import aioredis
import rating_system
import redis

import config
import storage
from helpers import models, locking
from storage import caching

_SELECT_SCORE_BY_TEAM_TASK_QUERY = "SELECT score from teamtasks WHERE team_id=%s AND task_id=%s AND round=%s"

_UPDATE_TEAMTASKS_SCORE_QUERY = "UPDATE teamtasks SET score = %s WHERE team_id=%s AND task_id=%s AND round >= %s"


def get_teams() -> List[models.Team]:
    """Get list of teams registered in the database"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        while True:
            try:
                pipeline.watch('teams:cached')
                cached = pipeline.exists('teams:cached')

                pipeline.multi()
                if not cached:
                    caching.cache_teams(pipeline)

                pipeline.execute()
                break
            except redis.WatchError:
                continue

        teams, = pipeline.smembers('teams').execute()
        teams = list(models.Team.from_json(team) for team in teams)

    return teams


async def get_teams_async(loop) -> List[models.Team]:
    """Get list of teams registered in the database (asynchronous version)"""

    redis_aio = await storage.get_async_redis_pool(loop)

    while True:
        try:
            await redis_aio.watch('teams:cached')

            cached = await redis_aio.exists('teams:cached')

            tr = redis_aio.multi_exec()
            if not cached:
                await caching.cache_teams_async(tr)

            await tr.execute()
            await redis_aio.unwatch()
            break
        except (aioredis.MultiExecError, aioredis.WatchVariableError):
            continue

    teams = await redis_aio.smembers('teams')
    teams = list(models.Team.from_json(team) for team in teams)

    return teams


def get_team_id_by_token(token: str) -> Optional[int]:
    """Get team by token

        :param token: token string
        :return: team id
    """

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('teams:cached').execute()
        if not cached:
            while True:
                try:
                    pipeline.watch('teams:cached')
                    cached = pipeline.exists('teams:cached')

                    pipeline.multi()
                    if not cached:
                        caching.cache_teams(pipeline)

                    pipeline.execute()
                    break
                except redis.WatchError:
                    continue

        team_id, = pipeline.get(f'team:token:{token}').execute()

    try:
        team_id = int(team_id.decode())
    except (ValueError, AttributeError):
        return None
    else:
        return team_id


def update_attack_team_ratings(attacker_id: int, victim_id: int, task_id: int, round: int) -> Tuple[float, float]:
    """Recalculate team ratings and update DB

        :param attacker_id: id of the attacking team
        :param victim_id: id of the victim team
        :param task_id: id of task which is attacked
        :param round: round of the attack

        :return: attacker & victim rating changes as tuple

        Possible race condition here (two flags with one rating delta), use with locks
    """
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    curs.execute(
        _SELECT_SCORE_BY_TEAM_TASK_QUERY,
        (
            attacker_id,
            task_id,
            round,
        ),
    )
    attacker_score, = curs.fetchone()

    curs.execute(
        _SELECT_SCORE_BY_TEAM_TASK_QUERY,
        (
            victim_id,
            task_id,
            round,
        ),
    )
    victim_score, = curs.fetchone()

    game_config = config.get_game_config()
    game_hardness = game_config.get('game_hardness')
    inflation = game_config.get('inflation')

    rs = rating_system.RatingSystem(
        attacker=attacker_score,
        victim=victim_score,
        game_hardness=game_hardness,
        inflation=inflation,
    )

    attacker_delta, victim_delta = rs.calculate()

    curs.execute(
        _UPDATE_TEAMTASKS_SCORE_QUERY,
        (
            attacker_score + attacker_delta,
            attacker_id,
            task_id,
            round,
        ),
    )
    curs.execute(
        _UPDATE_TEAMTASKS_SCORE_QUERY,
        (
            victim_score + victim_delta,
            victim_id,
            task_id,
            round,
        ),
    )

    conn.commit()
    curs.close()
    storage.get_db_pool().putconn(conn)

    return attacker_delta, victim_delta


def handle_attack(attacker_id: int, victim_id: int, task_id: int, round: int) -> float:
    """Lock team for update, call rating recalculation,
        then publish redis message about stolen flag

        :param attacker_id: id of the attacking team
        :param victim_id: id of the victim team
        :param task_id: id of task which is attacked
        :param round: round of the attack

        :return: attacker rating change
    """

    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        # Deadlock is our enemy
        min_team_id = min(attacker_id, victim_id)
        max_team_id = max(attacker_id, victim_id)

        with locking.acquire_redis_lock(pipeline, f'team:{min_team_id}:locked'):
            with locking.acquire_redis_lock(pipeline, f'team:{max_team_id}:locked'):
                attacker_delta, victim_delta = update_attack_team_ratings(
                    attacker_id=attacker_id,
                    victim_id=victim_id,
                    task_id=task_id,
                    round=round,
                )

        flag_data = {
            'attacker_id': attacker_id,
            'victim_id': victim_id,
            'attacker_delta': attacker_delta,
            'victim_delta': victim_delta,
        }

        pipeline.publish('stolen_flags', json.dumps(flag_data)).execute()

    return attacker_delta
