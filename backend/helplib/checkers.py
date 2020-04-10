from typing import Optional

import helplib
from helplib import models
from helplib.commands import run_generic_command
from helplib.thread_actions import run_generic_action_in_thread
from helplib.types import TaskStatus, Action


def first_error_or_first_verdict(verdicts: [models.CheckerVerdict]) -> Optional[models.CheckerVerdict]:
    if not verdicts:
        return None

    for verdict in verdicts:
        if verdict.status != TaskStatus.UP:
            return verdict

    return verdicts[0]


class CheckerRunner:
    """Helper class """
    team: models.Team
    task: models.Task
    flag: helplib.models.Flag

    def __init__(self, team, task, logger, flag=None):
        self.team = team
        self.task = task
        self.logger = logger
        self.flag = flag

    def check(self) -> helplib.models.CheckerVerdict:
        if self.task.is_checker_gevent_optimized:
            return self._check_in_thread()
        return self._check_as_process()

    def put(self) -> helplib.models.CheckerVerdict:
        if self.task.is_checker_gevent_optimized:
            return self._put_in_thread()
        return self._put_as_process()

    def get(self) -> helplib.models.CheckerVerdict:
        if self.task.is_checker_gevent_optimized:
            return self._get_in_thread()
        return self._get_as_process()

    def _check_as_process(self) -> helplib.models.CheckerVerdict:
        """Check implementation using subprocess calling"""
        check_command = [
            self.task.checker,
            'check',
            self.team.ip,
        ]

        return run_generic_command(
            command=check_command,
            action=Action.CHECK,
            env_path=self.task.env_path,
            timeout=self.task.checker_timeout,
            team_name=self.team.name,
            logger=self.logger,
        )

    def _put_as_process(self) -> helplib.models.CheckerVerdict:
        """Put implementation using subprocess calling"""

        put_command = [
            self.task.checker,
            'put',
            self.team.ip,
            self.flag.private_flag_data,
            self.flag.flag,
            str(self.flag.vuln_number),
        ]

        return run_generic_command(
            command=put_command,
            action=Action.PUT,
            env_path=self.task.env_path,
            timeout=self.task.checker_timeout,
            team_name=self.team.name,
            logger=self.logger,
        )

    def _get_as_process(self) -> helplib.models.CheckerVerdict:
        """Get implementation using subprocess calling"""

        get_command = [
            self.task.checker,
            'get',
            self.team.ip,
            self.flag.private_flag_data,
            self.flag.flag,
            str(self.flag.vuln_number),
        ]

        return run_generic_command(
            command=get_command,
            action=Action.GET,
            env_path=self.task.env_path,
            timeout=self.task.checker_timeout,
            team_name=self.team.name,
            logger=self.logger
        )

    def _check_in_thread(self) -> helplib.models.CheckerVerdict:
        """Check implementation, gevent-compatible"""

        return run_generic_action_in_thread(
            checker_path=self.task.checker,
            task_name=self.task.name,
            action=Action.CHECK,
            host=self.team.ip,
            team_name=self.team.name,
            timeout=self.task.checker_timeout,
            logger=self.logger,
            action_args=(),
            action_kwargs={},
        )

    def _put_in_thread(self) -> helplib.models.CheckerVerdict:
        """Check implementation, gevent-compatible"""

        kwargs = {
            'flag_id': self.flag.private_flag_data,
            'flag': self.flag.flag,
            'vuln': str(self.flag.vuln_number),
        }

        return run_generic_action_in_thread(
            checker_path=self.task.checker,
            task_name=self.task.name,
            action=Action.PUT,
            host=self.team.ip,
            team_name=self.team.name,
            timeout=self.task.checker_timeout,
            logger=self.logger,
            action_args=(),
            action_kwargs=kwargs,
        )

    def _get_in_thread(self) -> helplib.models.CheckerVerdict:
        """Check implementation, gevent-compatible"""

        kwargs = {
            'flag_id': self.flag.private_flag_data,
            'flag': self.flag.flag,
            'vuln': str(self.flag.vuln_number),
        }

        return run_generic_action_in_thread(
            checker_path=self.task.checker,
            task_name=self.task.name,
            action=Action.GET,
            host=self.team.ip,
            team_name=self.team.name,
            timeout=self.task.checker_timeout,
            logger=self.logger,
            action_args=(),
            action_kwargs=kwargs,
        )
