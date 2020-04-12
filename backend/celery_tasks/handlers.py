from celery import shared_task
from celery.utils.log import get_task_logger
from typing import List

import storage.tasks
from helplib import models, checkers
from helplib.types import TaskStatus, Action

logger = get_task_logger(__name__)


@shared_task
def exception_callback(result, exc, traceback):
    action_name = result.task.split('.')[-1].split('_')[0].upper()
    action = Action[action_name]

    kw = result.kwargs
    team, task, round = kw['team'], kw['task'], kw['round']

    if action == Action.CHECK:
        prev_verdict = None
    else:
        prev_verdict, = result.args

    logger.error(
        f"Task exception handler was called for team {team} task {task}, round {round}, "
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
            private_message=f'Exception on {action}: {repr(exc)}\n{traceback}'
        )

    storage.tasks.update_task_status(
        task_id=task.id,
        team_id=team.id,
        checker_verdict=verdict,
        round=round,
    )
    return verdict


@shared_task
def checker_results_handler(
        verdicts: List[models.CheckerVerdict],
        team: models.Team,
        task: models.Task,
        round: int) -> models.CheckerVerdict:
    """Parse returning verdicts and return the final one

        If there were any errors, the first one'll be returned
        Otherwise, verdict of the first (sequentially) action will be returned
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
            logger.error(f'Got invalid verdict action: {verdict.to_dict()}')

    logger.info(
        f"Finished testing team `{team.name}` task `{task.name}` round {round}. "
        f"Verdicts: check: {check_verdict} puts {puts_verdicts} gets {gets_verdict}"
    )

    parsed_verdicts = []
    if check_verdict is not None:
        parsed_verdicts.append(check_verdict)
    parsed_verdicts.extend(puts_verdicts)
    if gets_verdict is not None:
        parsed_verdicts.append(gets_verdict)

    result_verdict = checkers.first_error_or_first_verdict(parsed_verdicts)
    storage.tasks.update_task_status(
        task_id=task.id,
        team_id=team.id,
        checker_verdict=result_verdict,
        round=round,
    )
    return result_verdict
