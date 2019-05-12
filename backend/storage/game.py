from typing import Optional

import storage
from helpers import models


def get_current_round() -> int:
    """Get current round"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        round, = pipeline.get('round').execute()
    try:
        round = round.decode()
        return int(round)
    except (AttributeError, ValueError):
        return -1


async def get_current_round_async(loop) -> int:
    """Get current round (asynchronous version)"""
    redis = await storage.get_async_redis_pool(loop)
    round = await redis.get('round')

    try:
        round = round.decode()
        return int(round)
    except (ValueError, AttributeError):
        return -1


def get_game_state() -> Optional[models.GameState]:
    """Get game state for current round"""
    round = get_current_round()
    if not round:
        return None

    team_tasks = storage.tasks.get_teamtasks(round)
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
