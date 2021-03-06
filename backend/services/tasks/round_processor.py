import itertools
import random
from typing import Optional, Any

from celery import Task
from celery.utils.log import get_task_logger
from kombu.utils import json as kjson

import modes
from lib import storage
from lib.helpers import locking

logger = get_task_logger(__name__)

_FULL_UPDATE_ROUND_TYPES = ['full', 'puts']
_GS_UPDATE_ROUND_TYPES = ['full', 'puts', 'check_gets']


def get_round_processor(
        round_type: str, task_id: Optional[int] = None
) -> 'RoundProcessor':
    """Get RoundProcessor instance for specified round type"""
    return RoundProcessor(round_type=round_type, task_id=task_id)


class RoundProcessor(Task):
    @property
    def name(self) -> str:
        tmp = f'tasks.round_processor.RoundProcessor_{self.round_type}'
        if self.task_id is not None:
            tmp += f'_{self.task_id}'
        return tmp

    def __init__(self, round_type: str, task_id: Optional[int]):
        self.round_type = round_type
        self.task_id = task_id

    def should_update_round(self) -> bool:
        return self.round_type in _FULL_UPDATE_ROUND_TYPES

    def should_update_game_state(self) -> bool:
        return self.round_type in _GS_UPDATE_ROUND_TYPES

    @staticmethod
    def update_game_state(current_round: int) -> None:
        if not current_round:
            return

        game_state = storage.game.construct_latest_game_state(
            current_round=current_round,
        )

        if not game_state.team_tasks:
            logger.info("Empty team tasks, not updating scoreboard")
            return

        logger.info(f'Publishing scoreboard for round {current_round}')
        with storage.utils.redis_pipeline() as pipe:
            pipe.set('game_state', game_state.to_json())
            pipe.execute()

        storage.utils.SIOManager.write_only().emit(
            event='update_scoreboard',
            data={'data': game_state.to_dict()},
            namespace='/game_events',
        )

    @staticmethod
    def update_round(finished_round: int) -> None:
        logger.info(f'Updating round to {finished_round + 1}')

        storage.game.set_round_start(r=finished_round + 1)
        storage.game.update_real_round_in_db(new_round=finished_round + 1)

        with storage.utils.redis_pipeline(transaction=True) as pipe:
            pipe.set('real_round', finished_round + 1).execute()

    @staticmethod
    def update_attack_data(current_round: int) -> None:
        logger.info(f'Updating attack data contents for round {current_round}')

        tasks = storage.tasks.get_tasks()
        tasks = list(filter(lambda x: x.checker_provides_public_flag_data, tasks))
        flags = storage.flags.get_attack_data(current_round, tasks)
        with storage.utils.redis_pipeline(transaction=True) as pipe:
            pipe.set('attack_data', kjson.dumps(flags)).execute()

    def run(self, *args: Any, **kwargs: Any) -> None:
        """
        Process new round.

        Updates current round variable, then processes all teams.
        This function also caches previous state and notifies frontend of
        a new round (for classic game mode).
        Only one instance of process_round that updates round is to be be run!
        """

        game_running = storage.game.get_game_running()
        if not game_running:
            logger.info('Game is not running, exiting')
            return

        with storage.utils.redis_pipeline() as pipe:
            with locking.acquire_redis_lock(pipe, locking.LockEnum.ROUND_UPDATE):
                current_round = storage.game.get_real_round_from_db()
                round_to_check = current_round

                if self.should_update_round():
                    self.update_round(current_round)
                    round_to_check = current_round + 1
                    self.update_attack_data(round_to_check)

        if not round_to_check:
            logger.info("Not processing, round is 0")
            return

        if self.should_update_game_state():
            self.update_game_state(current_round)

        teams = storage.teams.get_teams()
        random.shuffle(teams)
        tasks = storage.tasks.get_tasks()
        random.shuffle(tasks)

        round_args = itertools.product(teams, tasks, [round_to_check])

        if self.round_type == 'full':
            logger.info("Running full round")
            modes.run_full_round.starmap(round_args).apply_async()
        elif self.round_type == 'check_gets':
            logger.info("Running check_gets round")
            modes.run_check_gets_round.starmap(round_args).apply_async()
        elif self.round_type == 'puts':
            logger.info("Running puts round")
            modes.run_puts_round.starmap(round_args).apply_async()
        else:
            logger.critical(
                'Invalid round type supplied: %s, falling back to full',
                self.round_type,
            )
            modes.run_full_round.starmap(round_args).apply_async()
