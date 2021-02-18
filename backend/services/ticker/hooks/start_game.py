import logging

from lib import storage

logger = logging.getLogger(__name__)


def set_started_if_not() -> bool:
    already_started = storage.game.get_game_running()
    if already_started:
        return False

    storage.game.set_round_start(r=0)
    storage.game.set_game_running(True)
    return True


def start_game(**_kwargs) -> None:
    """Starts game

    Sets `game_running` in DB
    """
    logger.info('Trying to start game')
    if not set_started_if_not():
        logger.info('Game already started')
        return

    logger.info('Updating game state for round 0')
    game_state = storage.game.update_game_state(for_round=0)
    logger.info('Initialized game state with %s', game_state.to_dict())
