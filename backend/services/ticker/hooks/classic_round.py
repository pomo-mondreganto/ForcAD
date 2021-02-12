import itertools
import logging
import random

from lib import storage

logger = logging.getLogger(__name__)


def update_round(finished_round: int) -> None:
    new_round = finished_round + 1

    storage.game.set_round_start(r=new_round)
    storage.game.update_real_round_in_db(new_round=new_round)

    with storage.utils.redis_pipeline(transaction=True) as pipe:
        pipe.set(storage.keys.CacheKeys.current_round(), new_round)
        pipe.execute()


def run_classic_round(state):
    current_round = storage.game.get_real_round_from_db()
    logger.info('Ending round %s', current_round)
    storage.game.update_round(current_round)

    round_to_check = current_round + 1

    if not round_to_check:
        logger.info('Not processing, round is 0')
        return

    logger.info('Updating attack data contents for round %s', round_to_check)
    storage.game.update_attack_data(round_to_check)

    teams = storage.teams.get_teams()
    tasks = storage.tasks.get_tasks()

    round_args = list(itertools.product(teams, tasks, [round_to_check]))
    random.shuffle(round_args)

    for each in round_args:
        state.celery_app.send_task('tasks.modes.run_full_round', args=each)
