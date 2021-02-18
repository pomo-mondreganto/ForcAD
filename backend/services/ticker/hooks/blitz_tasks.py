import logging
from copy import deepcopy
from typing import Callable

from celery import Celery
from celery.canvas import chain, group

from lib import storage, models
from . import utils

logger = logging.getLogger(__name__)


def submit_puts_jobs(app: Celery, team: models.Team, task: models.Task, r: int):
    kwargs, params = utils.get_round_setup(app, team, task, r)

    handler = utils.get_result_handler_signature(app, kwargs)

    put_kwargs = deepcopy(kwargs)
    put_kwargs['_prev_verdict'] = None
    puts = utils.get_puts_group(app, task, put_kwargs, params)
    scheme = chain(puts, handler)
    scheme.apply_async()


def submit_check_gets_jobs(app: Celery, team: models.Team, task: models.Task, r: int):
    kwargs, params = utils.get_round_setup(app, team, task, r)

    handler = utils.get_result_handler_signature(app, kwargs)
    check = utils.get_check_signature(app, kwargs, params)
    noop = utils.get_noop_signature(app)
    gets = utils.get_gets_chain(app, task, kwargs, params)
    scheme = chain(check, group([noop, gets]), handler)
    scheme.apply_async()


def run_blitz_puts_round(state):
    new_round = utils.update_round()
    if not new_round:
        return

    args_list = utils.get_round_processor_args(new_round)

    for args in args_list:
        submit_puts_jobs(state.celery_app, *args)


def blitz_check_gets_runner_factory(task_id: int) -> Callable:
    def run_blitz_check_gets_round(state):
        current_round = storage.game.get_real_round()
        if current_round < 1:
            return

        args_list = utils.get_round_processor_args(current_round, task_id=task_id)

        for args in args_list:
            submit_puts_jobs(state.celery_app, *args)

    return run_blitz_check_gets_round
