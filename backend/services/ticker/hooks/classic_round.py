import logging

from celery import Celery
from celery.canvas import chain, group

from lib import models
from . import utils

logger = logging.getLogger(__name__)


def submit_full_round_jobs(app: Celery, team: models.Team, task: models.Task, r: int):
    kwargs, params = utils.get_round_setup(app, team, task, r)

    check = utils.get_check_signature(app, kwargs, params)
    noop = utils.get_noop_signature(app)
    puts = utils.get_puts_group(app, task, kwargs, params)
    gets = utils.get_gets_chain(app, task, kwargs, params)

    handler = utils.get_result_handler_signature(app, kwargs)

    scheme = chain(
        check,
        group([noop, puts, gets]),  # noop task is required to pass check result forward
        handler,
    )
    scheme.apply_async()


def run_classic_round(state):
    new_round = utils.update_round()
    if not new_round:
        return

    args_list = utils.get_round_processor_args(new_round)

    for args in args_list:
        submit_full_round_jobs(state.celery_app, *args)
