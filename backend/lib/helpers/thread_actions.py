import importlib.util
from logging import Logger
from traceback import format_exc

import gevent

from lib import models
from lib.helpers import exceptions
from lib.models import TaskStatus, Action


def set_verdict_error(verdict: models.CheckerVerdict, action: Action, message: str):
    verdict.status = TaskStatus.CHECK_FAILED
    verdict.public_message = f'{action} failed'
    verdict.private_message = message


def run_generic_action_in_thread(
        action: Action,
        task: models.Task,
        team: models.Team,
        action_args: tuple,
        action_kwargs: dict,
        logger: Logger,
) -> models.CheckerVerdict:
    verdict = models.CheckerVerdict(
        command=f'checker.{action}()',
        action=action,
        status=TaskStatus.CHECK_FAILED,
        public_message=f'{action} pending',
        private_message=f'{action} pending',
    )

    try:
        spec = importlib.util.spec_from_file_location(task.name, task.checker)
        checker_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker_module)  # type: ignore
        checker = checker_module.Checker(team.ip)  # type: ignore
        finished_exception = checker.get_check_finished_exception()
    except BaseException as e:
        tb = format_exc()
        exc = f'{type(e)}: {e}\n{tb}'

        message = (
            'Exception while importing checker. '
            'Your checker is not compatible with "gevent" checker tag. '
            f'Exception: {exc}'
        )

        logger.critical(message)

        set_verdict_error(verdict=verdict, action=action, message=message)
        return verdict

    try:
        with gevent.Timeout(task.checker_timeout, exceptions.CheckerTimeoutException):
            checker.action(action.name.lower(), *action_args, **action_kwargs)

    except finished_exception:
        try:
            verdict.status = TaskStatus(checker.status)
        except ValueError:
            mess = (
                f'Invalid TaskStatus: {checker.status} for '
                f'team `{team.id}` task `{task.id}`'
            )
            logger.error(mess)

            set_verdict_error(verdict=verdict, action=action, message=mess)
        else:
            verdict.public_message = checker.public
            verdict.private_message = checker.private

    except exceptions.CheckerTimeoutException:
        logger.warning('%s for team %s task %s timed out', action, team.id, task.id)

        verdict.status = TaskStatus.DOWN
        verdict.public_message = 'Checker timed out'
        verdict.private_message = f'Checker for {action} timed out'

    except BaseException as e:
        tb = format_exc()
        exc = f'{type(e)}: {e}\n{tb}'

        logger.error(
            '%s for team %s task %s failed with %s',
            action,
            team.id,
            task.id,
            exc,
        )

        set_verdict_error(verdict=verdict, action=action, message=exc)

    else:
        mess = 'Checker did not raise CheckFinished'
        logger.error(mess)
        set_verdict_error(verdict=verdict, action=action, message=mess)

    return verdict
