import os
import subprocess
from typing import Tuple

import helpers.models
import helpers.status
from helpers.status import TaskStatus


def run_command_gracefully(*popenargs,
                           input=None,
                           capture_output=False,
                           timeout=None,
                           check=False,
                           terminate_timeout=1,
                           **kwargs):
    if input is not None:
        kwargs['stdin'] = subprocess.PIPE

    if capture_output:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE

    with subprocess.Popen(*popenargs, **kwargs) as proc:
        try:
            stdout, stderr = proc.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                stdout, stderr = proc.communicate(input, timeout=terminate_timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
            except:
                proc.kill()
                raise

            raise subprocess.TimeoutExpired(
                proc.args,
                timeout=timeout,
                output=stdout,
                stderr=stderr,
            )
        except:
            proc.kill()
            raise

        retcode = proc.poll()

        if check and retcode:
            raise subprocess.CalledProcessError(
                retcode,
                proc.args,
                output=stdout,
                stderr=stderr
            )

    return subprocess.CompletedProcess(proc.args, retcode, stdout, stderr)


def run_check_command(checker_path: str,
                      env_path: str,
                      host: str,
                      team_name: str,
                      timeout: int,
                      logger) -> Tuple[helpers.status.TaskStatus, str]:
    check_command = [
        checker_path,
        'check',
        host,
    ]

    env = os.environ.copy()
    env['PATH'] = f"{env_path}:{env['PATH']}"

    try:
        check_result = run_command_gracefully(
            check_command,
            capture_output=True,
            timeout=timeout,
            env=env,
        )

        try:
            status = TaskStatus(check_result.returncode)
            message = check_result.stderr[:1024].decode().strip()
        except ValueError:
            status = TaskStatus.CHECK_FAILED
            message = 'Check failed'
            logger.warning(
                f'Check of team {team_name} failed with exit code {check_result.returncode}, '
                f'stdout: {check_result.stdout}\nstderr: {check_result.stderr}'
            )

    except subprocess.TimeoutExpired:
        status = TaskStatus.DOWN
        message = 'Check timeout'

    return status, message


def run_put_command(checker_path: str,
                    env_path: str,
                    host: str,
                    place: int,
                    flag: helpers.models.Flag,
                    team_name: str,
                    timeout: int,
                    logger) -> Tuple[helpers.status.TaskStatus, str]:
    put_command = [
        checker_path,
        'put',
        host,
        'lolkek',
        flag.flag,
        str(place),
    ]

    env = os.environ.copy()
    env['PATH'] = f"{env_path}:{env['PATH']}"

    try:
        put_result = run_command_gracefully(
            put_command,
            capture_output=True,
            timeout=timeout,
            env=env,
        )

        try:
            status = TaskStatus(put_result.returncode)
            message = put_result.stderr[:1024].decode().strip()
        except ValueError:
            status = TaskStatus.CHECK_FAILED
            message = 'Check failed'
            logger.warning(
                f'Put for team {team_name} failed with exit code {put_result.returncode}, '
                f'stderr: {put_result.stderr}'
            )

    except subprocess.TimeoutExpired:
        status = TaskStatus.DOWN
        message = 'Put timeout'

    return status, message


def run_get_command(checker_path: str,
                    env_path: str,
                    host: str,
                    flag: helpers.models.Flag,
                    team_name: str,
                    timeout: int,
                    logger) -> Tuple[helpers.status.TaskStatus, str]:
    get_command = [
        checker_path,
        'get',
        host,
        flag.flag_data,
        flag.flag,
    ]

    env = os.environ.copy()
    env['PATH'] = f"{env_path}:{env['PATH']}"

    try:
        get_result = run_command_gracefully(
            get_command,
            capture_output=True,
            timeout=timeout,
            env=env,
        )

        try:
            status = TaskStatus(get_result.returncode)
            message = get_result.stderr[:1024].decode().strip()
        except ValueError:
            status = TaskStatus.CHECK_FAILED
            message = 'Check failed'
            logger.warning(
                f'Get for team {team_name} failed with exit code {get_result.returncode}, '
                f'stderr: {get_result.stderr}'
            )

    except subprocess.TimeoutExpired:
        status = TaskStatus.DOWN
        message = 'Get timeout'

    return status, message
