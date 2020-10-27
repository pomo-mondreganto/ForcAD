from logging import Logger
from traceback import format_exc

import gevent
import importlib.util

from lib import models
from lib.helpers import exceptions
from lib.models import TaskStatus, Action


def set_verdict_error(verdict: models.CheckerVerdict,
                      action: Action,
                      message: str) -> None:
    verdict.status = TaskStatus.CHECK_FAILED
    verdict.public_message = f'{action} failed'
    verdict.private_message = message


def run_generic_action_in_thread(checker_path: str,
                                 task_name: str,
                                 action: Action,
                                 host: str,
                                 team_name: str,
                                 timeout: int,
                                 action_args: tuple,
                                 action_kwargs: dict,
                                 logger: Logger) -> models.CheckerVerdict:
    verdict = models.CheckerVerdict(
        command=f'checker.{action}()',
        action=action,
        status=TaskStatus.CHECK_FAILED,
        public_message=f'{action} pending',
        private_message=f'{action} pending',
    )

    try:
        spec = importlib.util.spec_from_file_location(task_name, checker_path)
        checker_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker_module)  # type: ignore
        checker = checker_module.Checker(host)  # type: ignore
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
        with gevent.Timeout(timeout, exceptions.CheckerTimeoutException):
            checker.action(action.name.lower(), *action_args, **action_kwargs)

    except finished_exception:
        try:
            verdict.status = TaskStatus(checker.status)
        except ValueError:
            mess = (
                f'Invalid TaskStatus: {checker.status} for '
                f'team `{team_name}` task `{task_name}`'
            )
            logger.error(mess)

            set_verdict_error(verdict=verdict, action=action, message=mess)
        else:
            verdict.public_message = checker.public
            verdict.private_message = checker.private

    except exceptions.CheckerTimeoutException:
        logger.warning(
            f'{action} action for team `{team_name}` task {task_name} '
            'timed out'
        )

        verdict.status = TaskStatus.DOWN
        verdict.public_message = 'Checker timed out'
        verdict.private_message = f'Checker for {action} timed out'

    except BaseException as e:
        tb = format_exc()
        exc = f'{type(e)}: {e}\n{tb}'

        log_func = logger.warning
        if not isinstance(e, Exception) and not isinstance(e, SystemExit):
            log_func = logger.error
        log_func(
            f'{action} action for team `{team_name}` task `{task_name}` '
            f'failed with exception {exc}'
        )

        set_verdict_error(verdict=verdict, action=action, message=exc)

    else:
        mess = 'Checker did not raise CheckFinished'
        logger.error(mess)
        set_verdict_error(verdict=verdict, action=action, message=mess)

    return verdict
