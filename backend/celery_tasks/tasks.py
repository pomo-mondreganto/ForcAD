import random
import secrets

import redis
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

    start_game.apply_async(
        eta=game_config['start_time'],
    )


@shared_task
def test_task():
    logger.info('Hello world!')


@shared_task
def check_action(team_json, task_json, round: int):
    """Run "check" checker action

    :param team_json: json-dumped team
    :param task_json: json-dumped task
    :param round: current round
    """
    team = models.Team.from_json(team_json)
    task = models.Task.from_json(task_json)

    logger.info(f'Running checker for team {team.id} task {task.id}')

    tmp_verdict = models.CheckerActionResult(
        status=TaskStatus.CHECK_FAILED,
        private_message='Check pending',
        public_message='',
        command=[],
    )

    storage.tasks.update_task_status(
        task_id=task.id,
        team_id=team.id,
        checker_verdict=tmp_verdict,
        round=round,
    )

    logger.info(f'Running CHECK for team {team.id} task {task.id}')

    checker_verdict = checkers.run_check_command(
        checker_path=task.checker,
        env_path=task.env_path,
        host=team.ip,
        team_name=team,
        logger=logger,
        timeout=task.checker_timeout,
    )

    if checker_verdict.status != TaskStatus.UP:
        storage.tasks.update_task_status(
            task_id=task.id,
            team_id=team.id,
            checker_verdict=checker_verdict,
            round=round,
        )
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

        checker_verdict, flag_id = checkers.run_put_command(
            checker_path=task.checker,
            env_path=task.env_path,
            host=team.ip,
            place=place,
            flag=flag,
            team_name=team.name,
            timeout=task.checker_timeout,
            logger=logger,
        )

        if checker_verdict.status == TaskStatus.UP:
            if task.checker_returns_flag_id:
                flag.flag_data = checker_verdict.private_message
            else:
                flag.flag_data = flag_id
            storage.flags.add_flag(flag)
        else:
            storage.tasks.update_task_status(
                task_id=task.id,
                team_id=team.id,
                checker_verdict=checker_verdict,
                round=round,
            )
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

    checker_verdict = models.CheckerActionResult(
        status=TaskStatus.UP,
        public_message='',
        private_message='',
        command=[],
    )

    for get_round in rounds_to_check:
        flag = storage.flags.get_random_round_flag(
            team_id=team.id,
            task_id=task.id,
            round=get_round,
            current_round=round,
        )

        if not flag:
            checker_verdict.status = TaskStatus.CORRUPT
            checker_verdict.private_message = f'No flags from round {get_round}'
            checker_verdict.public_message = f'Could not get flag'
        else:
            checker_verdict = checkers.run_get_command(
                checker_path=task.checker,
                env_path=task.env_path,
                host=team.ip,
                flag=flag,
                team_name=team.name,
                timeout=task.checker_timeout,
                logger=logger,
            )

        if checker_verdict.status != TaskStatus.UP:
            break

    storage.tasks.update_task_status(
        task_id=task.id,
        team_id=team.id,
        checker_verdict=checker_verdict,
        round=round,
    )


@shared_task
def run_checker(team_json, task_json, round):
    """Run check, put and get"""
    chained = chain(
        check_action.s(team_json, task_json, round),
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

    logger.info(f'Processing round {new_round}')

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

    storage.tasks.initialize_teamtasks(round=new_round)

    teams = storage.teams.get_teams()
    for team in teams:
        process_team.delay(team.to_json(), new_round)


@shared_task
def start_game():
    """Starts game

    Sets `game_running` in DB
    """
    logger.info('Starting game')

    with storage.get_redis_storage().pipeline() as pipeline:
        while True:
            try:
                pipeline.watch('game_starting_lock')

                already_started = storage.game.get_game_running()
                if already_started:
                    logger.info('Game already started')
                    return
                storage.game.set_game_running(1)

                break
            except redis.WatchError:
                continue

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
