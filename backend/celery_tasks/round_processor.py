import random

import itertools
# noinspection PyProtectedMember
from celery import Task
from celery.utils.log import get_task_logger

import celery_tasks.modes
import storage

logger = get_task_logger(__name__)


class RoundProcessor(Task):
    _global_config = None
    name = 'celery_tasks.round_processor.RoundProcessor'

    @property
    def global_config(self):
        if self._global_config is None:
            self._global_config = storage.game.get_current_global_config()
        return self._global_config

    def update_game_state(self, finished_round):
        if self.global_config.game_mode != 'classic':
            return

        if finished_round:
            storage.caching.cache_teamtasks(round=finished_round)

        game_state = storage.game.construct_game_state(round=finished_round)
        if not game_state:
            logger.warning(f'Game state is missing for round {finished_round}, skipping')
        else:
            logger.info(f'Publishing scoreboard for round {finished_round}')
            with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
                pipeline.publish('scoreboard', game_state.to_json())
                pipeline.set('game_state', game_state.to_json())
                pipeline.execute()

    def run(self, *args, **kwargs):
        """Process new round
            Updates current round variable, then processes all teams.
            This function also caches previous state and notifies frontend of a new round (for classic game mode).
            Only one instance of process_round is to be be run!
        """

        game_running = storage.game.get_game_running()
        if not game_running:
            logger.info('Game is not running, exiting')
            return

        current_round = storage.game.get_real_round_from_db()
        finished_round = current_round

        logger.info(f'Processing round {finished_round + 1}')

        storage.game.set_round_start(round=finished_round + 1)
        storage.game.update_real_round_in_db(new_round=finished_round + 1)
        storage.tasks.initialize_teamtasks(round=finished_round + 1)

        # Might think there's a RC here (I thought so too)
        # But all teamtasks with round >= real_round are updated in the attack handler
        # So both old and new teamtasks will be updated properly
        with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
            pipeline.set('round', finished_round)
            pipeline.set('real_round', finished_round + 1)
            pipeline.execute()

        self.update_game_state(finished_round)

        teams = storage.teams.get_teams()
        random.shuffle(teams)
        tasks = storage.tasks.get_tasks()
        random.shuffle(tasks)

        args = itertools.product(teams, tasks, [finished_round + 1])

        mode = self.global_config.game_mode
        if mode == 'classic':
            logger.info("Applying classic game mode")
            celery_tasks.modes.apply_classic.starmap(args).apply_async()
        elif mode == 'blitz':
            logger.info("Applying blitz game mode")
            celery_tasks.modes.apply_blitz.starmap(args).apply_async()
        else:
            logger.critical(f"Invalid game_mode supplied: {mode}, falling back to classic")
            celery_tasks.modes.apply_classic.starmap(args).apply_async()
