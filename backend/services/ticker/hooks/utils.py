import itertools
import logging
import random
from typing import List, Tuple

from celery import Celery
from celery.canvas import signature, group, chain

from lib import storage, models
from lib.helpers.jobs import JobNames

logger = logging.getLogger(__name__)


def get_round_processor_args(r: int, **kwargs) -> List[tuple]:
    teams = storage.teams.get_teams()
    tasks = storage.tasks.get_tasks()

    if 'task_id' in kwargs:
        tasks = list(filter(lambda task: task.id == kwargs['task_id'], tasks))

    round_args = list(itertools.product(teams, tasks, [r]))
    random.shuffle(round_args)

    return round_args


def get_noop_signature(app: Celery) -> signature:
    return app.signature(JobNames.noop_action)


def get_check_signature(app: Celery, kwargs: dict, params: dict) -> signature:
    return app.signature(JobNames.check_action, kwargs=kwargs, **params)


def get_puts_group(app: Celery, task: models.Task, kwargs: dict, params: dict) -> group:
    signatures = [
        app.signature(JobNames.put_action, kwargs=kwargs, **params)
        for _ in range(task.puts)
    ]
    return group(*signatures)


def get_gets_chain(app: Celery, task: models.Task, kwargs: dict, params: dict) -> chain:
    signatures = [
        app.signature(JobNames.get_action, kwargs=kwargs, **params)
        for _ in range(task.gets)
    ]
    return chain(*signatures)


def get_result_handler_signature(app: Celery, kwargs: dict) -> signature:
    return app.signature(JobNames.result_handler, kwargs=kwargs)


def get_round_setup(
        app: Celery,
        team: models.Team,
        task: models.Task,
        current_round: int) -> Tuple[dict, dict]:
    params = {
        'time_limit': task.checker_timeout + 5,
        'link_error': app.signature(JobNames.error_handler),
    }
    kwargs = {
        'team': team,
        'task': task,
        'current_round': current_round,
    }
    return kwargs, params


def update_round() -> int:
    current_round = storage.game.get_real_round_from_db()
    logger.info('Ending round %s', current_round)
    storage.game.update_round(current_round)
    logger.info('Updating game state for round %s', current_round)
    storage.game.update_game_state(current_round)

    round_to_check = current_round + 1

    if not round_to_check:
        logger.info('Not processing, round is 0')
        return 0

    logger.info('Updating attack data contents for round %s', current_round)
    storage.game.update_attack_data(current_round)

    return round_to_check
