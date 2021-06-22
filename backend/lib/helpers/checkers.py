from logging import Logger
from typing import Optional

from lib import models
from lib.helpers.commands import run_generic_command
from lib.helpers.thread_actions import run_generic_action_in_thread
from lib.models import Action


class CheckerRunner:
    """Helper class """

    team: models.Team
    task: models.Task
    flag: Optional[models.Flag]

    def __init__(
            self,
            team: models.Team,
            task: models.Task,
            logger: Logger,
            flag: Optional[models.Flag] = None,
    ):
        self.team = team
        self.task = task
        self.logger = logger
        self.flag = flag

    def check(self) -> models.CheckerVerdict:
        if self.task.is_checker_gevent_optimized:
            return self._check_in_thread()
        return self._check_as_process()

    def put(self) -> models.CheckerVerdict:
        if self.task.is_checker_gevent_optimized:
            return self._put_in_thread()
        return self._put_as_process()

    def get(self) -> models.CheckerVerdict:
        if self.task.is_checker_gevent_optimized:
            return self._get_in_thread()
        return self._get_as_process()

    def _check_as_process(self) -> models.CheckerVerdict:
        """Check implementation using subprocess calling"""
        check_command = [
            self.task.checker,
            'check',
            self.team.ip,
        ]

        return run_generic_command(
            command=check_command,
            action=Action.CHECK,
            task=self.task,
            team=self.team,
            logger=self.logger,
        )

    def _put_as_process(self) -> models.CheckerVerdict:
        """Put implementation using subprocess calling"""
        assert self.flag is not None, 'Can only be called when flag is passed'

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
            task=self.task,
            team=self.team,
            logger=self.logger,
        )

    def _get_as_process(self) -> models.CheckerVerdict:
        """Get implementation using subprocess calling"""
        assert self.flag is not None, 'Can only be called when flag is passed'

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
            task=self.task,
            team=self.team,
            logger=self.logger,
        )

    def _check_in_thread(self) -> models.CheckerVerdict:
        """Check implementation, gevent-compatible"""

        return run_generic_action_in_thread(
            action=Action.CHECK,
            task=self.task,
            team=self.team,
            logger=self.logger,
            action_args=(),
            action_kwargs={},
        )

    def _put_in_thread(self) -> models.CheckerVerdict:
        """Check implementation, gevent-compatible"""
        assert self.flag is not None, 'Can only be called when flag is passed'

        kwargs = {
            'flag_id': self.flag.private_flag_data,
            'flag': self.flag.flag,
            'vuln': str(self.flag.vuln_number),
        }

        return run_generic_action_in_thread(
            action=Action.PUT,
            task=self.task,
            team=self.team,
            logger=self.logger,
            action_args=(),
            action_kwargs=kwargs,
        )

    def _get_in_thread(self) -> models.CheckerVerdict:
        """Check implementation, gevent-compatible"""
        assert self.flag is not None, 'Can only be called when flag is passed'

        kwargs = {
            'flag_id': self.flag.private_flag_data,
            'flag': self.flag.flag,
            'vuln': str(self.flag.vuln_number),
        }

        return run_generic_action_in_thread(
            action=Action.GET,
            task=self.task,
            team=self.team,
            logger=self.logger,
            action_args=(),
            action_kwargs=kwargs,
        )
