from celery import chain, group, shared_task
from celery.utils.log import get_task_logger

import celery_tasks.actions
import celery_tasks.auxiliary
import celery_tasks.handlers
from helplib import models

logger = get_task_logger(__name__)


@shared_task
def run_full_round(team: models.Team, task: models.Task, round: int) -> bool:
    params = {
        'time_limit': task.checker_timeout + 5,
        'link_error': celery_tasks.handlers.exception_callback,
    }
    kwargs = {
        'team': team,
        'task': task,
        'round': round,
    }

    check = celery_tasks.actions.check_action.s(**kwargs).set(**params)

    puts = group([
        celery_tasks.actions.put_action.s(**kwargs).set(**params)
        for _ in range(task.puts)
    ])

    gets = chain(*[
        celery_tasks.actions.get_action.s(**kwargs).set(**params)
        for _ in range(task.gets)
    ])

    handler = celery_tasks.handlers.checker_results_handler.s(**kwargs)

    scheme = chain(check, group([celery_tasks.actions.noop, puts, gets]), handler)
    scheme.apply_async()

    return True


@shared_task
def run_puts_round(team: models.Team, task: models.Task, round: int) -> bool:
    params = {
        'time_limit': task.checker_timeout + 5,
        'link_error': celery_tasks.handlers.exception_callback,
    }
    kwargs = {
        'team': team,
        'task': task,
        'round': round,
    }
    puts = group([
        celery_tasks.actions.put_action.s(_checker_verdict_code=None, **kwargs).set(**params)
        for _ in range(task.puts)
    ])
    handler = celery_tasks.handlers.checker_results_handler.s(**kwargs)
    scheme = chain(puts, handler)
    scheme.apply_async()

    return True


@shared_task
def run_check_gets_round(team: models.Team, task: models.Task, round: int) -> bool:
    params = {
        'time_limit': task.checker_timeout + 5,
        'link_error': celery_tasks.handlers.exception_callback,
    }
    kwargs = {
        'team': team,
        'task': task,
        'round': round,
    }
    check = celery_tasks.actions.check_action.s(**kwargs).set(**params)
    gets = chain(*[
        celery_tasks.actions.get_action.s(**kwargs).set(**params)
        for _ in range(task.gets)
    ])
    handler = celery_tasks.handlers.checker_results_handler.s(**kwargs)
    scheme = chain(check, group([celery_tasks.actions.noop, gets]), handler)
    scheme.apply_async()

    return True
