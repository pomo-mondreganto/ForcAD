from celery import shared_task
from celery.utils.log import get_task_logger

from lib import storage
from lib.helpers import locking

logger = get_task_logger(__name__)


@shared_task
def start_game() -> None:
    """Starts game

    Sets `game_running` in DB
    """
    logger.info('Starting game')

    with storage.utils.redis_pipeline(transaction=True) as pipe:
        with locking.acquire_redis_lock(pipe, locking.LockEnum.GAME_START):
            already_started = storage.game.get_game_running()
            if already_started:
                logger.info('Game already started')
                return

            storage.game.set_round_start(r=0)
            storage.game.set_game_running(True)

        game_state = storage.game.construct_game_state_from_db(current_round=0)
        if not game_state:
            logger.warning('Initial game_state missing')
        else:
            logger.info(f"Initializing game_state with {game_state.to_dict()}")
            pipe.set(storage.keys.CacheKeys.game_state(), game_state.to_json())
            pipe.execute()

            storage.utils.SIOManager.write_only().emit(
                event='update_scoreboard',
                data={'data': game_state.to_dict()},
                namespace='/game_events',
            )
