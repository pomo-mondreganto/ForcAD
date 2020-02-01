import importlib.util
from traceback import format_exc

import gevent

import helplib


def set_verdict_error(verdict, action_name, message):
    verdict.status = helplib.status.TaskStatus.CHECK_FAILED
    verdict.public_message = f'{action_name} failed'
    verdict.private_message = message


def run_generic_action_in_thread(checker_path: str,
                                 task_name: str,
                                 action_name: str,
                                 host: str,
                                 team_name: str,
                                 timeout: int,
                                 action_args: tuple,
                                 action_kwargs: dict,
                                 logger):
    spec = importlib.util.spec_from_file_location(task_name, checker_path)
    checker_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker_module)
    checker = checker_module.Checker(host)
    finished_exception = checker.get_check_finished_exception()

    verdict = helplib.models.CheckerVerdict(
        command=f'checker.{action_name.lower()}()',
        action=action_name,
        status=helplib.status.TaskStatus.CHECK_FAILED,
        public_message=f'{action_name} pending',
        private_message=f'{action_name} pending',
    )

    try:
        with gevent.Timeout(timeout, helplib.exceptions.CheckerTimeoutException):
            checker.action(action_name.lower(), *action_args, **action_kwargs)

    except finished_exception:
        try:
            verdict.status = helplib.status.TaskStatus(checker.status)
        except ValueError:
            mess = f'Invalid TaskStatus: {checker.status} for team `{team_name}` task `{task_name}`'
            logger.error(mess)

            set_verdict_error(
                verdict=verdict,
                action_name=action_name,
                message=mess,
            )
        else:
            verdict.public_message = checker.public
            verdict.private_message = checker.private

    except helplib.exceptions.CheckerTimeoutException:
        logger.warning(f'{action_name} action for team `{team_name}` task {task_name} timed out')

        verdict.status = helplib.status.TaskStatus.DOWN
        verdict.public_message = 'Checker timed out'
        verdict.private_message = f'Checker for {action_name} timed out'

    except BaseException as e:
        tb = format_exc()
        exc = f'{type(e)}: {e}\n{tb}'

        log_func = logger.warning
        if not isinstance(e, Exception) and not isinstance(e, SystemExit):
            log_func = logger.error
        log_func(f'{action_name} action for team `{team_name}` task `{task_name}` failed with exception {exc}')

        set_verdict_error(
            verdict=verdict,
            action_name=action_name,
            message=exc,
        )

    else:
        mess = 'Checker did not raise CheckFinished'
        logger.error(mess)

        set_verdict_error(
            verdict=verdict,
            action_name=action_name,
            message=mess,
        )

    return verdict
