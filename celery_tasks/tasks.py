import os
import random
import secrets

from celery import shared_task, chain
from celery.signals import worker_ready
from celery.utils.log import get_task_logger

import config
import storage
from helpers import checkers, flags, models
from helpers.status import TaskStatus

logger = get_task_logger(__name__)


@worker_ready.connect
def startup(**_kwargs):
    """Task to run on start of celery, schedules game start"""
    game_config = config.get_game_config()

    logger.info(f'Received game config: {game_config}')

    start_game.apply_async(args=(), eta=game_config['start_time'])


@shared_task
def test_task():
    logger.info('Hello world!')


@shared_task
def check_action(team_json, task_json):
    """Run "check" checker action

    :param team_json: json-dumped team
    :param task_json: json-dumped task
    """
    team = models.Team.from_json(team_json)
    task = models.Task.from_json(task_json)

    logger.info(f'Running checker for team {team.id} task {task.id}')

    storage.tasks.update_task_status(
        task_id=task.id,
        team_id=team.id,
        status=TaskStatus.CHECK_FAILED,
        message='Check pending',
    )

    logger.info(f'Running CHECK for team {team.id} task {task.id}')

    status, message = checkers.run_check_command(
        checker_path=task.checker,
        env_path=task.env_path,
        host=team.ip,
        team_name=team,
        logger=logger,
        timeout=task.checker_timeout,
    )

    if status != TaskStatus.UP:
        storage.tasks.update_task_status(task_id=task.id, team_id=team.id, status=status, message=message)
        return False

    return True


@shared_task
def put_action(check_ok, team_json, task_json, round):
    """Run "put" checker action

        :param check_ok: boolean passed by "check" action in chain to indicate successful check
        :param team_json: json-dumped team
        :param task_json: json-dumped task
        :param round: current round

        If "check" action fails, put is not run.

        It runs `task.puts` times, each time new flag is generated.
    """
    if not check_ok:
        return False

    team = models.Team.from_json(team_json)
    task = models.Task.from_json(task_json)

    logger.info(f'Running PUT {task.puts} time(s) for team {team.id} task {task.id}')

    ok = True
    for i in range(task.puts):
        place = secrets.choice(range(1, task.places + 1))
        flag = flags.generate_flag(
            service=task.name[0].upper(),
            team_id=team.id,
            task_id=task.id,
            round=round,
        )

        status, message = checkers.run_put_command(
            checker_path=task.checker,
            env_path=task.env_path,
            host=team.ip,
            place=place,
            flag=flag,
            team_name=team.name,
            timeout=task.checker_timeout,
            logger=logger,
        )

        if status == TaskStatus.UP:
            flag.flag_data = message
            storage.flags.add_flag(flag)
        else:
            storage.tasks.update_task_status(task_id=task.id, team_id=team.id, status=status, message=message)
            ok = False
            break

    return ok


@shared_task
def get_action(put_ok, team_json, task_json, round):
    """Run "get" checker action

        :param put_ok: boolean passed by "put" action in chain to indicate successful check and put
        :param team_json: json-dumped team
        :param task_json: json-dumped task
        :param round: current round

        If "check" or "put" actions fail, get is not run.

        It runs `task.gets` times, each time a flag is chosen randomly from last "flag_lifetime" rounds
    """
    if not put_ok:
        return False

    team = models.Team.from_json(team_json)
    task = models.Task.from_json(task_json)

    flag_lifetime = config.get_game_config()['flag_lifetime']

    rounds_to_check = list(set(max(1, round - x) for x in range(0, flag_lifetime)))
    random.shuffle(rounds_to_check)
    rounds_to_check = rounds_to_check[:task.gets]

    logger.info(f'Running GET on rounds {rounds_to_check} for team {team.id} task {task.id}')

    status = TaskStatus.UP
    message = ''

    for get_round in rounds_to_check:
        try:
            flag = storage.flags.get_random_round_flag(
                team_id=team.id,
                task_id=task.id,
                round=get_round,
                current_round=round
            )

            status, message = checkers.run_get_command(
                checker_path=task.checker,
                env_path=task.env_path,
                host=team.ip,
                flag=flag,
                team_name=team.name,
                timeout=task.checker_timeout,
                logger=logger,
            )
        except IndexError:
            status = TaskStatus.CORRUPT
            message = f'No flags from round {get_round}'

        if status != TaskStatus.UP:
            break

    storage.tasks.update_task_status(task_id=task.id, team_id=team.id, status=status, message=message)


@shared_task
def run_checker(team_json, task_json, round):
    """Run check, put and get"""
    chained = chain(
        check_action.s(team_json, task_json),
        put_action.s(team_json, task_json, round),
        get_action.s(team_json, task_json, round),
    )

    chained.apply_async()


@shared_task
def process_team(team_json, round):
    """Run checkers for all team tasks"""
    tasks = storage.tasks.get_tasks()
    for task in tasks:
        run_checker.delay(team_json, task.to_json(), round)


@shared_task
def process_round():
    """Process new round

        Updated current round variable, then processes all teams.
        This function also caches previous state and notifies frontend of a new round.
    """
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        game_running, = pipeline.get('game_running').execute()
        if not game_running:
            logger.info('Game is not running, exiting')
            return

    try:
        with open(os.path.join(config.BASE_DIR, 'volumes/shared/round')) as f:
            current_round = int(f.read())

    except FileNotFoundError or ValueError:
        current_round = 1
        with open(os.path.join(config.BASE_DIR, 'volumes/shared/round'), 'w') as f:
            f.write('2')
    else:
        with open(os.path.join(config.BASE_DIR, 'volumes/shared/round'), 'w') as f:
            f.write(f'{current_round + 1}')

    logger.info(f'Processing round {current_round}')

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.set('round', current_round - 1)
        pipeline.execute()

    if current_round > 1:
        storage.caching.cache_teamtasks(current_round - 1)

    game_state = storage.game.get_game_state()
    if not game_state:
        logger.warning(f'Game state is missing for round {current_round - 1}, skipping')
    else:
        with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
            pipeline.publish('scoreboard', game_state.to_json())
            pipeline.set('game_state', game_state.to_json())
            pipeline.execute()

    teams = storage.teams.get_teams()
    for team in teams:
        process_team.delay(team.to_json(), current_round)


@shared_task
def start_game():
    """Starts game

    Sets `game_running` boolean in cache
    """
    logger.info('Starting game')

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        already_started, = pipeline.exists('game_running').execute()
        if already_started:
            logger.info('Game already started')
            return

        pipeline.set('game_running', 1).execute()
