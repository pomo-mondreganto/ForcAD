import random
import secrets

from celery import shared_task

import storage
from celery_tasks.auxiliary import logger
from helplib import models, flags, checkers
from helplib.types import TaskStatus, Action


@shared_task
def noop(data):
    """Helper task to return checker verdict"""
    return data


@shared_task
def put_action(_checker_verdict_code: int, team: models.Team, task: models.Task, round: int) -> models.CheckerVerdict:
    """Run "put" checker action

        :param _checker_verdict_code: integer verdict code passed by check action in chain
        :param team: models.Team instance
        :param task: models.Task instance
        :param round: current round
        :returns verdict: models.CheckerVerdict instance

        If "check" action fails, put is not run.
    """

    logger.info(f'Running PUT for team `{team.name}` task `{task.name}`')

    place = secrets.choice(range(1, task.places + 1))
    flag = flags.generate_flag(
        service=task.name[0].upper(),
        team_id=team.id,
        task_id=task.id,
        round=round,
    )
    flag.private_flag_data = secrets.token_hex(20)
    flag.vuln_number = place

    runner = checkers.CheckerRunner(team=team, task=task, flag=flag, logger=logger)

    verdict = runner.put()

    if verdict.status == TaskStatus.UP:
        flag = task.set_flag_data(flag, verdict)
        storage.flags.add_flag(flag)

    return verdict


@shared_task
def get_action(prev_verdict: models.CheckerVerdict, team: models.Team, task: models.Task,
               round) -> models.CheckerVerdict:
    """Run "get" checker action

        :param prev_verdict: verdict passed by previous check or get in chain
        :param team: models.Team instance
        :param task: models.Task instance
        :param round: current round
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
            private_message=f'Previous returned {prev_verdict}'
        )

        return new_verdict

    flag_lifetime = storage.game.get_current_global_config().flag_lifetime

    rounds_to_check = list(set(max(1, round - x) for x in range(0, flag_lifetime)))
    round_to_check = random.choice(rounds_to_check)

    logger.info(f'Running GET on round {round_to_check} for team {team.id} task {task.id}')

    verdict = models.CheckerVerdict(
        status=TaskStatus.UP,
        public_message='',
        private_message='',
        action=Action.GET,
        command="",
    )

    flag = storage.flags.get_random_round_flag(
        team_id=team.id,
        task_id=task.id,
        round=round_to_check,
        current_round=round,
    )

    if not flag:
        verdict.status = TaskStatus.UP
        verdict.private_message = f'No flag from round {round_to_check}'
    else:
        runner = checkers.CheckerRunner(team=team, task=task, flag=flag, logger=logger)
        verdict = runner.get()

    return verdict


@shared_task
def check_action(team: models.Team, task: models.Task, round: int) -> models.CheckerVerdict:
    """Run "check" checker action

    :param team: models.Team instance
    :param task: models.Task instance
    :param round: current round (for exception handler)

    :return verdict: models.CheckerVerdict instance
    """

    logger.info(f'Running CHECK for team `{team.name}` task `{task.name}`, round {round}')
    runner = checkers.CheckerRunner(team=team, task=task, logger=logger)
    verdict = runner.check()

    return verdict
