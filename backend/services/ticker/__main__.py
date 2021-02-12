import logging
import time
from datetime import timedelta, datetime

import pytz

from lib import storage, models
from services.tasks import get_celery_app
from . import hooks
from .models import TickerState, Schedule

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)


def bootstrap_state() -> TickerState:
    with storage.utils.db_cursor() as (_, curs):
        already_started = storage.game.get_game_running()
    celery_app = get_celery_app()
    return TickerState(
        game_started=already_started,
        celery_app=celery_app,
    )


def bootstrap_schedules(state: TickerState):
    game_config = storage.game.get_current_global_config()
    if game_config.game_mode == models.GameMode.CLASSIC:
        start_schedule = Schedule(
            schedule_id='start_game',
            start=game_config.start_time,
            func=hooks.start_game,
        )
        start_schedule.load_last_run()
        state.register_schedule(start_schedule)

        round_interval = timedelta(seconds=game_config.round_time)
        rounds_schedule = Schedule(
            schedule_id='classic_rounds',
            start=game_config.start_time,
            func=hooks.run_classic_round,
            interval=round_interval,
        )
        rounds_schedule.load_last_run()
        state.register_schedule(rounds_schedule)

    elif game_config.game_mode == models.GameMode.BLITZ:
        # TODO: add blitz schedule
        pass


def main(state: TickerState):
    game_config = storage.game.get_current_global_config()
    tz = pytz.timezone(game_config.timezone)
    while True:
        now = tz.localize(datetime.now())
        due_schedules = state.get_due_schedules(now)
        for schedule in due_schedules:
            logger.info('Executing schedule %s', schedule.schedule_id)
            schedule.execute(state=state)
            schedule.last_run = now
            schedule.save_last_run()
        time.sleep(0.1)  # 100ms precision


if __name__ == '__main__':
    ticker_state = bootstrap_state()
    bootstrap_schedules(ticker_state)
    main(ticker_state)
