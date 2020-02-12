# noinspection PyProtectedMember
import random

from celery import Task, chain, group
from celery.utils.log import get_task_logger

import celery_tasks.actions
import celery_tasks.handlers
import celery_tasks.tasks
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

    @staticmethod
    def apply_classic(teams, tasks, round):
        for task in tasks:
            params = {
                'time_limit': task.checker_timeout + 5,
                'link_error': celery_tasks.handlers.exception_callback,
            }
            for team in teams:
                kwargs = {
                    'team': team,
                    'task': task,
                    'round': round,
                }

                check = celery_tasks.actions.check_action.s(**kwargs).set(**params)

                puts = group([
                    celery_tasks.actions.put_action.s(**kwargs).set(**params)
                    for _ in range(task.puts)
                ])

                gets = chain(*[
                    celery_tasks.actions.get_action.s(**kwargs).set(**params)
                    for _ in range(task.gets)
                ])

                handler = celery_tasks.handlers.classic_checker_results_handler.s(**kwargs)

                scheme = chain(check, group([celery_tasks.actions.noop, puts, gets]), handler)
                scheme.apply_async()

    def apply_blitz(self, tasks, teams, round):
        raise NotImplementedError

    def apply_checkers(self, teams, tasks, round):
        mode = self.global_config.game_mode
        if mode == 'classic':
            logger.info("Applying classic game mode")
            self.apply_classic(teams, tasks, round)
        elif mode == 'blitz':
            logger.info("Applying blitz game mode")
            self.apply_blitz(teams, tasks, round)
        else:
            logger.critical(f"Invalid game_mode supplied: {mode}, falling back to classic")
            self.apply_classic(teams, tasks, round)

    def run(self, *args, **kwargs):
        """Process new round

                Updates current round variable, then processes all teams.
                This function also caches previous state and notifies frontend of a new round.

                Only one instance of process_round is to be be run!
            """

        game_running = storage.game.get_game_running()
        if not game_running:
            logger.info('Game is not running, exiting')
            return

        current_round = storage.game.get_real_round_from_db()
        finished_round = current_round
        new_round = current_round + 1

        storage.game.set_round_start(round=new_round)
        storage.game.update_real_round_in_db(new_round=new_round)
        storage.tasks.initialize_teamtasks(round=new_round)

        logger.info(f'Processing round {new_round}')

        # Might think there's a RC here (I thought so too)
        # But all teamtasks with round >= real_round are updated in the attack handler
        # So both old and new teamtasks will be updated properly
        with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
            pipeline.set('round', finished_round)
            pipeline.set('real_round', new_round)
            pipeline.execute()

        if new_round > 1:
            storage.caching.cache_teamtasks(round=finished_round)

        game_state = storage.game.construct_game_state(round=finished_round)
        print(f'Got game state: {game_state.to_dict()}')
        if not game_state:
            logger.warning(f'Game state is missing for round {finished_round}, skipping')
        else:
            logger.info(f'Publishing scoreboard for round {finished_round}')
            with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
                pipeline.publish('scoreboard', game_state.to_json())
                pipeline.set('game_state', game_state.to_json())
                pipeline.execute()

        teams = storage.teams.get_teams()
        random.shuffle(teams)
        tasks = storage.tasks.get_tasks()
        random.shuffle(tasks)

        self.apply_checkers(teams=teams, tasks=tasks, round=new_round)
