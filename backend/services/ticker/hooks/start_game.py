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

    game_state = storage.game.construct_game_state_from_db(current_round=0)
    if not game_state:
        logger.warning('Initial game state missing')
        return

    logger.info('Initializing game state with %s', game_state.to_dict())

    with storage.utils.redis_pipeline(transaction=False) as pipe:
        pipe.set(storage.keys.CacheKeys.game_state(), game_state.to_json())
        pipe.execute()

    storage.utils.SIOManager.write_only().emit(
        event='update_scoreboard',
        data={'data': game_state.to_dict()},
        namespace='/game_events',
    )
