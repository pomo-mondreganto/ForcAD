from typing import List

from celery import shared_task
from celery.result import AsyncResult
from celery.utils.log import get_task_logger

from lib import storage, models
from lib.helpers.jobs import JobNames
from lib.models import TaskStatus, Action

logger = get_task_logger(__name__)


@shared_task(name=JobNames.error_handler)
def exception_callback(result: AsyncResult, exc: Exception, traceback: str) -> None:
    action_name = result.task.split('.')[-1].split('_')[0].upper()
    action = Action[action_name]

    kw = result.kwargs
    team, task, current_round = kw['team'], kw['task'], kw['current_round']

    if action == Action.CHECK:
        prev_verdict = None
    else:
        prev_verdict, = result.args

    logger.error(
        f"Task exception handler was called for "
        f"team {team} task {task}, round {current_round}, "
        f"exception {repr(exc)}, traceback\n{traceback}"
    )

    if prev_verdict is not None and prev_verdict.status != TaskStatus.UP:
        verdict = prev_verdict
    else:
        verdict = models.CheckerVerdict(
            action=action,
            status=TaskStatus.CHECK_FAILED,
            command='',
            public_message=f'{action} failed',
            private_message=f'Exception on {action}: {repr(exc)}\n{traceback}',
        )

    storage.tasks.update_task_status(
        task_id=task.id,
        team_id=team.id,
        current_round=current_round,
        checker_verdict=verdict,
    )
    return verdict


@shared_task(name=JobNames.result_handler)
def checker_results_handler(
        verdicts: List[models.CheckerVerdict],
        team: models.Team,
        task: models.Task,
        current_round: int,
) -> models.CheckerVerdict:
    """
    Parse returning verdicts and return the final one.

    If there were any errors, the first error is returned
    Otherwise, verdict of the first action's verdict is returned.
    """
    check_verdict = None
    puts_verdicts = []
    gets_verdict = None
    for verdict in verdicts:
        if verdict.action == Action.CHECK:
            check_verdict = verdict
        elif verdict.action == Action.GET:
            gets_verdict = verdict
        elif verdict.action == Action.PUT:
            puts_verdicts.append(verdict)
        else:
            logger.error('Got invalid verdict action: %s', verdict.to_dict())

    logger.info(
        "Finished testing team %s task %s, round %s.\n"
        "Verdicts: check: %s; puts: %s; gets: %s.",
        team.id,
        task.id,
        current_round,
        check_verdict,
        puts_verdicts,
        gets_verdict,
    )

    parsed_verdicts = []
    if check_verdict is not None:
        parsed_verdicts.append(check_verdict)
    parsed_verdicts.extend(puts_verdicts)
    if gets_verdict is not None:
        parsed_verdicts.append(gets_verdict)

    if verdicts:
        try:
            result_verdict = next(filter(
                lambda x: x.status != TaskStatus.UP,
                verdicts,
            ))
        except StopIteration:
            result_verdict = verdicts[0]
    else:
        logger.critical('No verdicts returned from actions!')
        result_verdict = models.CheckerVerdict(
            public_message='Checker failed',
            private_message='No verdicts passed to handler',
            command='',
            status=TaskStatus.CHECK_FAILED,
            action=Action.CHECK,
        )

    storage.tasks.update_task_status(
        task_id=task.id or 0,
        team_id=team.id or 0,
        current_round=current_round,
        checker_verdict=result_verdict,
    )
    return result_verdict
