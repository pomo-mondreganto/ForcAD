import os
import secrets
import subprocess
from typing import Tuple, List

import helplib
from helplib.status import TaskStatus


def run_command_gracefully(*popenargs,
                           input=None,
                           capture_output=False,
                           timeout=None,
                           check=False,
                           terminate_timeout=3,
                           **kwargs):
    """Wrapper around Popen from subprocess, shuts the process down gracefully

        First sends SIGTERM, waits for "terminate_timeout" seconds and if
        the timeout occurs the second time, sends SIGKILL.

        It's similar to "run" function from subprocess module.

        :param input: see corresponding "run" parameter
        :param capture_output: see corresponding "run" parameter
        :param timeout: "soft" timeout, after which the SIGTERM is sent
        :param check: see corresponding "run" parameter
        :param terminate_timeout: the "hard" timeout to wait after the SIGTERM
        :return: tuple of CompletedProcess instance and "killed" boolean
    """
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


def get_patched_environ(env_path: str):
    """Add path to the environment variable

        :param env_path: path to be inserted to environment
    """
    env = os.environ.copy()
    env['PATH'] = f"{env_path}:{env['PATH']}"
    return env


def run_generic_command(command: List,
                        command_type: str,
                        env_path: str,
                        timeout: int,
                        team_name: str,
                        logger) -> helplib.models.CheckerVerdict:
    """Run generic checker command, calls "run_command_gracefully" and handles exceptions

    :param command: command to run
    :param command_type: type of command (for logging)
    :param env_path: path to insert into environment
    :param timeout: "soft" command timeout
    :param team_name: team name for logging
    :param logger: logger instance
    :return: CheckerActionResult instance
    """
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
            public_message = result.stdout[:1024].decode().strip()
            private_message = result.stderr[:1024].decode().strip()
            if status == TaskStatus.CHECK_FAILED:
                logger.warning(
                    f'{command_type.upper()} for team {team_name} failed with exit code {result.returncode},'
                    f'\nstderr: {result.stderr},\nstdout: {result.stdout}'
                )
        except ValueError:
            status = TaskStatus.CHECK_FAILED
            public_message = 'Check failed'
            private_message = 'Check failed'
            logger.warning(
                f'{command_type.upper()} for team {team_name} failed with exit code {result.returncode},'
                f'\nstderr: {result.stderr},\nstdout: {result.stdout}'
            )

    except subprocess.TimeoutExpired:
        status = TaskStatus.DOWN
        private_message = f'{command_type.upper()} timeout'
        public_message = 'Timeout'

    result = helplib.models.CheckerVerdict(
        public_message=public_message,
        private_message=private_message,
        command=command,
        status=status
    )

    return result


def run_check_command(checker_path: str,
                      env_path: str,
                      host: str,
                      team_name: str,
                      timeout: int,
                      logger) -> helplib.models.CheckerVerdict:
    """Runs "check" command

        :param checker_path: absolute checker path
        :param env_path: path to insert into environment
        :param host: team host
        :param team_name: team name for logging
        :param timeout: "soft" timeout
        :param logger: logger instance
        :return: CheckerActionResult instance
    """
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
                    flag: helplib.models.Flag,
                    team_name: str,
                    timeout: int,
                    logger) -> Tuple[helplib.models.CheckerVerdict, str]:
    """Runs "put" command

        :param checker_path: absolute checker path
        :param env_path: path to insert into environment
        :param host: team host
        :param place: flag place for large tasks
        :param flag: Flag model instance to put
        :param team_name: team name for logging
        :param timeout: "soft" timeout
        :param logger: logger instance
        :return: tuple of CheckerActionResult instance and generated flag_id
    """

    flag_id = secrets.token_hex(20)

    put_command = [
        checker_path,
        'put',
        host,
        flag_id,
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
    ), flag_id


def run_get_command(checker_path: str,
                    env_path: str,
                    host: str,
                    flag: helplib.models.Flag,
                    team_name: str,
                    timeout: int,
                    logger) -> helplib.models.CheckerVerdict:
    """Runs "put" command

        :param checker_path: absolute checker path
        :param env_path: path to insert into environment
        :param host: team host
        :param flag: Flag model instance to put
        :param team_name: team name for logging
        :param timeout: "soft" timeout
        :param logger: logger instance
        :return: CheckerActionResult instance
    """
    get_command = [
        checker_path,
        'get',
        host,
        flag.flag_data,
        flag.flag,
        str(flag.vuln_number),
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
