from celery import shared_task
from celery.signals import worker_ready
from celery.utils.log import get_task_logger

import storage
from helplib import locking

logger = get_task_logger(__name__)


@worker_ready.connect
def startup(**_kwargs):
    """Task to run on start of celery, schedules game start"""
    game_config = storage.game.get_current_global_config()

    logger.info(f'Received game config: {game_config}')

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        with locking.acquire_redis_lock(pipeline, 'game_starting_lock'):
            already_started = storage.game.get_game_running()

            if not already_started:
                logger.info("Game is not running, initializing...")
                start_game.apply_async(
                    eta=game_config.start_time,
                )

                game_state = storage.game.construct_game_state_from_db(round=0)
                if not game_state:
                    logger.warning('Initial game_state missing')
                else:
                    logger.info(f"Initializing game_state with {game_state.to_dict()}")
                    pipeline.set('game_state', game_state.to_json())
                    pipeline.execute()

                    storage.get_wro_sio_manager().emit(
                        event='update_scoreboard',
                        data={'data': game_state.to_dict()},
                        namespace='/game_events',
                    )


@shared_task
def start_game():
    """Starts game

    Sets `game_running` in DB
    """
    logger.info('Starting game')

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        with locking.acquire_redis_lock(pipeline, 'game_starting_lock'):
            already_started = storage.game.get_game_running()
            if already_started:
                logger.info('Game already started')
                return

            storage.game.set_round_start(round=0)
            storage.game.set_game_running(True)

        game_state = storage.game.construct_game_state_from_db(round=0)
        if not game_state:
            logger.warning('Initial game_state missing')
        else:
            logger.info(f"Initializing game_state with {game_state.to_dict()}")
            pipeline.set('game_state', game_state.to_json())
            pipeline.execute()

            storage.get_wro_sio_manager().emit(
                event='update_scoreboard',
                data={'data': game_state.to_dict()},
                namespace='/game_events',
            )
