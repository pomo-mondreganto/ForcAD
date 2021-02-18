import random
import secrets
from typing import Optional, Any

from celery import shared_task
from celery.utils.log import get_task_logger

from lib import models, storage
from lib.helpers import checkers
from lib.helpers.jobs import JobNames
from lib.models import TaskStatus, Action

logger = get_task_logger(__name__)


@shared_task(name=JobNames.noop_action)
def noop(data: Any) -> Any:
    """Helper task to return checker verdict"""
    return data


@shared_task(name=JobNames.put_action)
def put_action(
        _prev_verdict: Optional[models.CheckerVerdict],
        team: models.Team,
        task: models.Task,
        current_round: int,
) -> models.CheckerVerdict:
    """
    Run "put" checker action.

    :param _prev_verdict: verdict passed by check action in chain
    :param team: models.Team instance
    :param task: models.Task instance
    :param current_round: current round
    :returns verdict: models.CheckerVerdict instance

    If "check" action fails, put is not run.
    """

    logger.info(
        'Running PUT for team %s task %s, round %s',
        team.id,
        task.id,
        current_round,
    )

    place = secrets.choice(range(1, task.places + 1))
    flag = models.Flag.generate(
        service=task.name[0].upper(),
        team_id=team.id or 0,
        task_id=task.id or 0,
        current_round=current_round,
    )
    flag.private_flag_data = secrets.token_hex(20)
    flag.vuln_number = place

    runner = checkers.CheckerRunner(
        team=team,
        task=task,
        flag=flag,
        logger=logger,
    )

    verdict = runner.put()

    if verdict.status == TaskStatus.UP:
        flag = task.set_flag_data(flag, verdict)
        storage.flags.add_flag(flag)

    return verdict


@shared_task(name=JobNames.get_action)
def get_action(
        prev_verdict: models.CheckerVerdict,
        team: models.Team,
        task: models.Task,
        current_round: int,
) -> models.CheckerVerdict:
    """
    Run "get" checker action.

    :param prev_verdict: verdict passed by previous check or get in chain
    :param team: models.Team instance
    :param task: models.Task instance
    :param current_round: current round
    :returns: previous result & self result

    If "check" or previous "get" actions fail, get is not run.
    """
    if prev_verdict.status != TaskStatus.UP:
        if prev_verdict.action == Action.GET:
            return prev_verdict

        # to avoid returning CHECK verdict
        new_verdict = models.CheckerVerdict(
            action=Action.GET,
            status=prev_verdict.status,
            command='',
            public_message='Skipped GET, previous action failed',
            private_message=f'Previous returned {prev_verdict}',
        )

        return new_verdict

    flag_lifetime = storage.game.get_current_game_config().flag_lifetime

    rounds_to_check = list(
        set(max(1, current_round - x) for x in range(0, flag_lifetime))
    )
    round_to_check = random.choice(rounds_to_check)

    logger.info(
        'Running GET on round %s for team %s task %s, current round %s',
        round_to_check,
        team.id,
        task.id,
        current_round,
    )

    verdict = models.CheckerVerdict(
        status=TaskStatus.UP,
        public_message='',
        private_message='',
        action=Action.GET,
        command="",
    )

    flag = storage.flags.get_random_round_flag(
        team_id=team.id or 0,
        task_id=task.id or 0,
        from_round=round_to_check,
        current_round=current_round,
    )

    if not flag:
        verdict.status = TaskStatus.UP
        verdict.private_message = f'No flag from round {round_to_check}'
    else:
        runner = checkers.CheckerRunner(
            team=team,
            task=task,
            flag=flag,
            logger=logger,
        )
        verdict = runner.get()

    return verdict


@shared_task(name=JobNames.check_action)
def check_action(
        team: models.Team, task: models.Task, current_round: int
) -> models.CheckerVerdict:
    """
    Run "check" checker action.

    :param team: models.Team instance
    :param task: models.Task instance
    :param current_round: current round (for exception handler)

    :return verdict: models.CheckerVerdict instance
    """

    logger.info(
        'Running CHECK for team %s task %s, round %s',
        team.id,
        task.id,
        current_round,
    )
    runner = checkers.CheckerRunner(team=team, task=task, logger=logger)
    verdict = runner.check()

    return verdict
