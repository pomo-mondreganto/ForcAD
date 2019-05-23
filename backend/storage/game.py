from typing import Optional

import storage
from helpers import models

_CURRENT_REAL_ROUND_QUERY = 'SELECT real_round FROM globalconfig WHERE id=1'

_UPDATE_REAL_ROUND_QUERY = 'UPDATE globalconfig SET real_round = %s WHERE id=1'

_SET_GAME_RUNNING_QUERY = 'UPDATE globalconfig SET game_running = %s WHERE id=1'

_GET_GAME_RUNNING_QUERY = 'SELECT game_running FROM globalconfig WHERE id=1'


def get_current_round() -> int:
    """Get current round, returns -1 if round not in cache"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        round, = pipeline.get('round').execute()

    try:
        round = int(round.decode())
    except (AttributeError, ValueError):
        return -1
    else:
        return round


def get_real_round() -> int:
    """Get real round of system (for flag submitting),
    returns -1 if round not in cache
    """
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
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
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()
    curs.execute(_CURRENT_REAL_ROUND_QUERY)
    round, = curs.fetchone()

    curs.close()
    storage.get_db_pool().putconn(conn)

    return round


def update_real_round_in_db(new_round: int):
    """Update real round stored in DB"""
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()
    curs.execute(_UPDATE_REAL_ROUND_QUERY, (new_round,))

    conn.commit()
    curs.close()
    storage.get_db_pool().putconn(conn)


def set_game_running(new_value: int):
    """Update game_running value in db"""
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()
    curs.execute(_SET_GAME_RUNNING_QUERY, (new_value,))

    conn.commit()
    curs.close()
    storage.get_db_pool().putconn(conn)


def get_game_running() -> int:
    """Update game_running value in db"""
    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()
    curs.execute(_GET_GAME_RUNNING_QUERY)
    game_running, = curs.fetchone()

    curs.close()
    storage.get_db_pool().putconn(conn)

    return game_running


async def get_current_round_async(loop) -> int:
    """Get current round (asynchronous version)"""
    redis = await storage.get_async_redis_pool(loop)
    round = await redis.get('round')

    try:
        round = round.decode()
        return int(round)
    except (ValueError, AttributeError):
        return -1


def get_game_state(round: Optional[int] = None) -> Optional[models.GameState]:
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

    state = models.GameState(round=round, team_tasks=team_tasks)
    return state


async def get_game_state_async(loop) -> Optional[models.GameState]:
    """Get game state for current round (asynchronous version)"""
    redis = await storage.get_async_redis_pool(loop)
    state = await redis.get('game_state')
    try:
        state = state.decode()
        state = models.GameState.from_json(state)
    except AttributeError:
        return None
    else:
        return state
