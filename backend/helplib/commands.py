import os
import shlex

import subprocess
from typing import List

import helplib
from helplib.types import TaskStatus, Action


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
                        action: Action,
                        env_path: str,
                        timeout: int,
                        team_name: str,
                        logger) -> helplib.models.CheckerVerdict:
    """Run generic checker command, calls "run_command_gracefully" and handles exceptions

    :param command: command to run
    :param action: type of command (for logging)
    :param env_path: path to insert into environment
    :param timeout: "soft" command timeout
    :param team_name: team name for logging
    :param logger: logger instance
    :return: models.CheckerVerdict instance
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
                f'Process was forcefully killed during {action} '
                f'for team {team_name} task '
            )

        try:
            status = TaskStatus(result.returncode)
            public_message = result.stdout[:1024].decode().strip()
            private_message = result.stderr[:1024].decode().strip()
            if status == TaskStatus.CHECK_FAILED:
                logger.warning(
                    f'{action} for team {team_name} failed with exit code {result.returncode},'
                    f'\nstderr: {result.stderr},\nstdout: {result.stdout}'
                )
        except ValueError as e:
            status = TaskStatus.CHECK_FAILED
            public_message = 'Check failed'
            private_message = f'Check failed with ValueError: {str(e)}'
            logger.warning(
                f'{action} for team {team_name} failed with exit code {result.returncode},'
                f'\nstderr: {result.stderr},\nstdout: {result.stdout}'
            )

    except subprocess.TimeoutExpired:
        status = TaskStatus.DOWN
        private_message = f'{action} timeout (killed by ForcAD)'
        public_message = 'Timeout'

    command_str = ' '.join(shlex.quote(x) for x in command)
    result = helplib.models.CheckerVerdict(
        public_message=public_message,
        private_message=private_message,
        command=command_str,
        action=action,
        status=status
    )

    return result
