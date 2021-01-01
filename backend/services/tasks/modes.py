from celery import chain, group, shared_task
from celery.utils.log import get_task_logger
from typing import Tuple

import actions
import handlers
from lib import models

logger = get_task_logger(__name__)


def get_round_setup(team: models.Team,
                    task: models.Task,
                    current_round: int) -> Tuple[dict, dict]:
    params = {
        'time_limit': task.checker_timeout + 5,
        'link_error': handlers.exception_callback,
    }
    kwargs = {
        'team': team,
        'task': task,
        'current_round': current_round,
    }
    return params, kwargs


def get_puts_group(task: models.Task, kwargs: dict, params: dict) -> group:
    return group([
        actions.put_action.s(**kwargs).set(**params)
        for _ in range(task.puts)
    ])


def get_gets_chain(task: models.Task, kwargs: dict, params: dict) -> group:
    return chain(*[
        actions.get_action.s(**kwargs).set(**params)
        for _ in range(task.gets)
    ])


@shared_task
def run_full_round(team: models.Team,
                   task: models.Task,
                   current_round: int) -> bool:
    params, kwargs = get_round_setup(team, task, current_round)
    check = actions.check_action.s(**kwargs).set(**params)

    puts = get_puts_group(task, kwargs, params)
    gets = get_gets_chain(task, kwargs, params)

    handler = handlers.checker_results_handler.s(**kwargs)

    scheme = chain(
        check,
        group([actions.noop, puts, gets]),
        handler,
    )
    scheme.apply_async()

    return True


@shared_task
def run_puts_round(team: models.Team,
                   task: models.Task,
                   current_round: int) -> bool:
    params, kwargs = get_round_setup(team, task, current_round)

    handler = handlers.checker_results_handler.s(**kwargs)

    kwargs['_prev_verdict'] = None
    puts = get_puts_group(task, kwargs, params)
    scheme = chain(puts, handler)
    scheme.apply_async()

    return True


@shared_task
def run_check_gets_round(team: models.Team,
                         task: models.Task,
                         current_round: int) -> bool:
    params, kwargs = get_round_setup(team, task, current_round)
    check = actions.check_action.s(**kwargs).set(**params)
    gets = get_gets_chain(task, kwargs, params)
    handler = handlers.checker_results_handler.s(**kwargs)
    scheme = chain(check, group([actions.noop, gets]), handler)
    scheme.apply_async()

    return True
