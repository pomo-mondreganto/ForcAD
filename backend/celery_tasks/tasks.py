import random
import secrets

from celery import shared_task, chain, group
from celery.signals import worker_ready
from celery.utils.log import get_task_logger
from typing import List

import config
import storage
from helplib import checkers, flags, models, locking
from helplib.status import TaskStatus

logger = get_task_logger(__name__)


@worker_ready.connect
def startup(**_kwargs):
    """Task to run on start of celery, schedules game start"""
    game_config = config.get_global_config()

    logger.info(f'Received game config: {game_config}')

    start_game.apply_async(
        eta=game_config['start_time'],
    )

    round = storage.game.get_real_round()
    if not round or round == -1:
        storage.caching.cache_teamtasks(round=0)

        game_state = storage.game.get_game_state(round=0)
        if not game_state:
            logger.warning('Initial game_state missing')
        else:
            with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
                logger.info(f"Initializing game_state with {game_state.to_dict()}")
                pipeline.set('game_state', game_state.to_json())
                pipeline.publish('scoreboard', game_state.to_json())
                pipeline.execute()


@shared_task
def test_task():
    logger.info('Hello world!')


@shared_task
def exception_callback(*args, **kwargs):
    logger.warning(f"Exception callback was called with args {args}, kwargs {kwargs}")


@shared_task
def check_action(team: models.Team, task: models.Task, round: int) -> models.CheckerVerdict:
    """Run "check" checker action

    :param team: models.Team instance
    :param task: models.Task instance
    :param round: current round

    :return verdict: models.CheckerVerdict instance
    """

    logger.info(f'Running CHECK for team `{team.name}` task `{task.name}`')
    runner = checkers.CheckerRunner(team=team, task=task, logger=logger)
    verdict = runner.check()

    return verdict


@shared_task
def noop(data):
    """Helper task to return checker verdict"""
    return data


@shared_task
def put_action(_checker_verdict_code: int, team: models.Team, task: models.Task, round: int) -> models.CheckerVerdict:
    """Run "put" checker action

        :param _checker_verdict_code: integer verdict code passed by check action in chain
        :param team: models.Team instance
        :param task: models.Task instance
        :param round: current round
        :returns verdict: models.CheckerVerdict instance

        If "check" action fails, put is not run.
    """

    logger.info(f'Running CHECK for team `{team.name}` task `{task.name}`')

    place = secrets.choice(range(1, task.places + 1))
    flag = flags.generate_flag(
        service=task.name[0].upper(),
        team_id=team.id,
        task_id=task.id,
        round=round,
    )
    flag.flag_data = secrets.token_hex(20)
    flag.vuln_number = place

    runner = checkers.CheckerRunner(team=team, task=task, flag=flag, logger=logger)

    verdict = runner.put()

    if verdict.status == TaskStatus.UP:
        if task.checker_returns_flag_id:
            flag.flag_data = verdict.public_message

        storage.flags.add_flag(flag)

    return verdict


@shared_task
def get_action(prev_verdict: models.CheckerVerdict, team: models.Team, task: models.Task,
               round) -> models.CheckerVerdict:
    """Run "get" checker action

        :param prev_verdict: verdict passed by previous check or get in chain
        :param team: models.Team instance
        :param task: models.Task instance
        :param round: current round
        :returns: previous result & self result

        If "check" or previous "get" actions fail, get is not run.

    """
    if prev_verdict.status != TaskStatus.UP:
        # to avoid returning CHECK verdict
        new_verdict = models.CheckerVerdict(
            action='GET',
            status=prev_verdict.status,
            command='',
            public_message='Skipped GET, previous action failed',
            private_message=f'Previous returned {prev_verdict}'
        )

        return new_verdict

    flag_lifetime = storage.game.get_current_global_config().flag_lifetime

    rounds_to_check = list(set(max(1, round - x) for x in range(0, flag_lifetime)))
    round_to_check = random.choice(rounds_to_check)

    logger.info(f'Running GET on round {round_to_check} for team {team.id} task {task.id}')

    verdict = models.CheckerVerdict(
        status=TaskStatus.UP,
        public_message='',
        private_message='',
        action='GET',
        command="",
    )

    flag = storage.flags.get_random_round_flag(
        team_id=team.id,
        task_id=task.id,
        round=round_to_check,
        current_round=round,
    )

    if not flag:
        verdict.status = TaskStatus.UP
        verdict.private_message = f'No flag from round {round_to_check}'
    else:
        runner = checkers.CheckerRunner(team=team, task=task, flag=flag, logger=logger)
        verdict = runner.get()

    return verdict


@shared_task
def checker_results_handler(verdicts: List[models.CheckerVerdict], team: models.Team, task: models.Task, round: int):
    check_verdict = None
    puts_verdicts = []
    gets_verdict = None
    for verdict in verdicts:
        if verdict.action.upper() == 'CHECK':
            check_verdict = verdict
        elif verdict.action.upper() == 'GET':
            gets_verdict = verdict
        elif verdict.action.upper() == 'PUT':
            puts_verdicts.append(verdict)
        else:
            logger.error(f'Got invalid verdict action: {verdict.to_dict()}')

    logger.info(
        f"Finished testing team `{team.name}` task `{task.name}`. "
        f"Verdicts: check: {check_verdict} puts {puts_verdicts} gets {gets_verdict}"
    )

    if check_verdict.status != TaskStatus.UP:
        storage.tasks.update_task_status(
            task_id=task.id,
            team_id=team.id,
            checker_verdict=check_verdict,
            round=round,
        )
        return

    for verdict in puts_verdicts:
        if verdict.status != TaskStatus.UP:
            storage.tasks.update_task_status(
                task_id=task.id,
                team_id=team.id,
                checker_verdict=verdict,
                round=round,
            )
            return

    if gets_verdict != TaskStatus.UP:
        storage.tasks.update_task_status(
            task_id=task.id,
            team_id=team.id,
            checker_verdict=gets_verdict,
            round=round,
        )
        return

    storage.tasks.update_task_status(
        task_id=task.id,
        team_id=team.id,
        checker_verdict=check_verdict,
        round=round,
    )


@shared_task
def process_round():
    """Process new round

        Updates current round variable, then processes all teams.
        This function also caches previous state and notifies frontend of a new round.

        Only one instance of process_round could be run!
    """

    game_running = storage.game.get_game_running()
    if not game_running:
        logger.info('Game is not running, exiting')
        return

    current_round = storage.game.get_real_round_from_db()
    finished_round = current_round
    new_round = current_round + 1
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

    game_state = storage.game.get_game_state(round=finished_round)
    if not game_state:
        logger.warning(f'Game state is missing for round {finished_round}, skipping')
    else:
        logger.info(f'Publishing scoreboard for round {finished_round}')
        with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
            pipeline.publish('scoreboard', game_state.to_json())
            pipeline.set('game_state', game_state.to_json())
            pipeline.execute()

    teams = storage.teams.get_teams()
    tasks = storage.tasks.get_tasks()
    for task in tasks:
        hard_timeout = task.checker_timeout + 5
        for team in teams:
            check = check_action.s(team, task, new_round).set(time_limit=hard_timeout)

            puts = group([
                put_action.s(team, task, new_round).set(time_limit=hard_timeout)
                for _ in range(task.puts)
            ])

            gets = chain(*[
                get_action.s(team, task, new_round).set(time_limit=hard_timeout)
                for _ in range(task.gets)
            ])

            handler = checker_results_handler.s(team, task, new_round)

            scheme = chain(check, group([noop, puts, gets]), handler)
            scheme.apply_async()


@shared_task
def start_game():
    """Starts game

    Sets `game_running` in DB
    """
    logger.info('Starting game')

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        with locking.acquire_redis_lock(pipeline, 'game_starting_lock'):
            already_started = storage.game.get_game_running()
            if already_started:
                logger.info('Game already started')
                return
            storage.game.set_game_running(True)

    storage.caching.cache_teamtasks(round=0)

    game_state = storage.game.get_game_state(round=0)
    if not game_state:
        logger.warning('Initial game_state missing')
    else:
        with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
            logger.info(f"Initializing game_state with {game_state.to_dict()}")
            pipeline.set('game_state', game_state.to_json())
            pipeline.publish('scoreboard', game_state.to_json())
            pipeline.execute()
