import os
import subprocess
from typing import Tuple, List

import helpers.models
import helpers.status
from helpers.status import TaskStatus


def run_command_gracefully(*popenargs,
                           input=None,
                           capture_output=False,
                           timeout=None,
                           check=False,
                           terminate_timeout=3,
                           **kwargs):
    if input is not None:
        kwargs['stdin'] = subprocess.PIPE

    if capture_output:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE

    killed = False
    with subprocess.Popen(*popenargs, **kwargs) as proc:
        try:
            stdout, stderr = proc.communicate(input, timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                stdout, stderr = proc.communicate(input, timeout=terminate_timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                killed = True
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

    return subprocess.CompletedProcess(proc.args, retcode, stdout, stderr), killed


def get_patched_environ(env_path):
    env = os.environ.copy()
    env['PATH'] = f"{env_path}:{env['PATH']}"
    return env


def run_generic_command(command: List,
                        command_type: str,
                        env_path: str,
                        timeout: int,
                        team_name: str,
                        logger):
    env = get_patched_environ(env_path=env_path)

    try:
        result, killed = run_command_gracefully(
            command,
            capture_output=True,
            timeout=timeout,
            env=env,
        )

        if killed:
            logger.warning(
                f'Process was forcefully killed during {command_type.upper()} '
                f'for team {team_name}'
            )

        try:
            status = TaskStatus(result.returncode)
            message = result.stderr[:1024].decode().strip()
        except ValueError:
            status = TaskStatus.CHECK_FAILED
            message = 'Check failed'
            logger.warning(
                f'{command_type.upper()} for team {team_name} failed with exit code {result.returncode},'
                f'\nstderr: {result.stderr},\nstdout: {result.stdout}'
            )

    except subprocess.TimeoutExpired:
        status = TaskStatus.DOWN
        message = f'{command_type.upper()} timeout'

    return status, message


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

    return run_generic_command(
        command=check_command,
        command_type='check',
        env_path=env_path,
        timeout=timeout,
        team_name=team_name,
        logger=logger,
    )


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

    return run_generic_command(
        command=put_command,
        command_type='put',
        env_path=env_path,
        timeout=timeout,
        team_name=team_name,
        logger=logger,
    )


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

    return run_generic_command(
        command=get_command,
        command_type='get',
        env_path=env_path,
        timeout=timeout,
        team_name=team_name,
        logger=logger
    )
