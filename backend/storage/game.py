import redis
import time
from typing import Optional

import storage
from helplib import models

_CURRENT_REAL_ROUND_QUERY = 'SELECT real_round FROM globalconfig WHERE id=1'

_UPDATE_REAL_ROUND_QUERY = 'UPDATE globalconfig SET real_round = %s WHERE id=1'

_SET_GAME_RUNNING_QUERY = 'UPDATE globalconfig SET game_running = %s WHERE id=1'

_GET_GAME_RUNNING_QUERY = 'SELECT game_running FROM globalconfig WHERE id=1'

_GET_GLOBAL_CONFIG_QUERY = 'SELECT * from globalconfig WHERE id=1'


def get_current_round() -> int:
    """Get current round, returns -1 if round not in cache"""
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        round, = pipeline.get('round').execute()

    try:
        round = int(round.decode())
    except (AttributeError, ValueError):
        return -1
    else:
        return round


def get_round_start(round: int) -> int:
    """Get start time for round as unix timestamp"""
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        start_time, = pipeline.get(f'round:{round}:start_time').execute()
    try:
        start_time = int(start_time.decode())
    except (AttributeError, UnicodeDecodeError, ValueError):
        start_time = 0
    return start_time


def set_round_start(round: int):
    """Set start time for round as str"""
    cur_time = int(time.time())
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        pipeline.set(f'round:{round}:start_time', cur_time).execute()


def get_real_round() -> int:
    """Get real round of system (for flag submitting),
    returns -1 if round not in cache
    """
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        round, = pipeline.get('real_round').execute()

    try:
        round = int(round.decode())
    except (AttributeError, ValueError):
        return -1
    else:
        return round


def get_real_round_from_db() -> int:
    """Get real round from database
        Fully persistent to use with game management"""
    with storage.db_cursor() as (conn, curs):
        curs.execute(_CURRENT_REAL_ROUND_QUERY)
        round, = curs.fetchone()

    return round


def update_real_round_in_db(new_round: int):
    """Update real round stored in DB"""

    with storage.db_cursor() as (conn, curs):
        curs.execute(_UPDATE_REAL_ROUND_QUERY, (new_round,))
        conn.commit()


def set_game_running(new_value: bool):
    """Update game_running value in db"""
    with storage.db_cursor() as (conn, curs):
        curs.execute(_SET_GAME_RUNNING_QUERY, (new_value,))
        conn.commit()


def get_game_running() -> bool:
    """Update game_running value in db"""
    with storage.db_cursor() as (conn, curs):
        curs.execute(_GET_GAME_RUNNING_QUERY)
        game_running, = curs.fetchone()

    return game_running


def get_db_global_config() -> models.GlobalConfig:
    """Get global config from database as it is. Do not use it to fetch round or game_running"""
    with storage.db_cursor(dict_cursor=True) as (conn, curs):
        curs.execute(_GET_GLOBAL_CONFIG_QUERY)
        result = curs.fetchone()

    result.pop('game_running')
    result.pop('real_round')

    return models.GlobalConfig.from_dict(result)


def get_current_global_config() -> models.GlobalConfig:
    """Get global config from cache is cached, otherwise cache it"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        while True:
            try:
                pipeline.watch('global_config:cached')
                cached = pipeline.exists('global_config:cached')

                pipeline.multi()
                if not cached:
                    storage.caching.cache_global_config(pipeline)

                pipeline.execute()
                break
            except redis.WatchError:
                continue

        result, = pipeline.get('global_config').execute()
        global_config = models.GlobalConfig.from_json(result)

    return global_config


async def get_current_round_async(loop) -> int:
    """Get current round (asynchronous version)"""
    redis_pool = await storage.get_async_redis_storage(loop)
    round = await redis_pool.get('round')

    try:
        round = round.decode()
        return int(round)
    except (ValueError, AttributeError):
        return -1


def construct_game_state(round: Optional[int] = None) -> Optional[models.GameState]:
    """Get game state for current round

        :param round: specify round to query manually. Otherwise, it'll be taken from cache
    """
    if round is None:
        round = get_current_round()
        if not round:
            return None

    team_tasks = storage.tasks.get_teamtasks_for_participants(round)
    if not team_tasks:
        return None

    round_start = get_round_start(round)
    state = models.GameState(round_start=round_start, round=round, team_tasks=team_tasks)
    return state


async def get_game_state_async(loop) -> Optional[models.GameState]:
    """Get game state for current round (asynchronous version)"""
    redis_pool = await storage.get_async_redis_storage(loop)
    state = await redis_pool.get('game_state')
    try:
        state = state.decode()
        state = models.GameState.from_json(state)
    except AttributeError:
        return None
    else:
        return state
