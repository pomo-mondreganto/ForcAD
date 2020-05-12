import time
from typing import Optional

import storage
from helplib import models
from helplib.cache import cache_helper, async_cache_helper
from helplib.exceptions import FlagSubmitException
from storage import caching

_CURRENT_REAL_ROUND_QUERY = 'SELECT real_round FROM globalconfig WHERE id=1'

_UPDATE_REAL_ROUND_QUERY = 'UPDATE globalconfig SET real_round = %s WHERE id=1'

_SET_GAME_RUNNING_QUERY = '''
UPDATE globalconfig SET game_running = %s WHERE id=1
'''

_GET_GAME_RUNNING_QUERY = 'SELECT game_running FROM globalconfig WHERE id=1'

_GET_GLOBAL_CONFIG_QUERY = 'SELECT * FROM globalconfig WHERE id=1'


def get_round_start(r: int) -> int:
    """Get start time for round as unix timestamp."""
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        start_time, = pipeline.get(f'round:{r}:start_time').execute()
    try:
        start_time = int(start_time)
    except (ValueError, TypeError):
        start_time = 0
    return start_time


def set_round_start(r: int):
    """Set start time for round as str."""
    cur_time = int(time.time())
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        pipeline.set(f'round:{r}:start_time', cur_time).execute()


def get_real_round() -> int:
    """
    Get real round of system (for flag submitting).

    :returns: -1 if round not in cache, else round
    """
    with storage.get_redis_storage().pipeline(transaction=False) as pipeline:
        round, = pipeline.get('real_round').execute()

    try:
        round = int(round)
    except (ValueError, TypeError):
        return -1
    return round


def get_real_round_from_db() -> int:
    """
    Get real round from database.

    Fully persistent to use with game management
    """
    with storage.db_cursor() as (_, curs):
        curs.execute(_CURRENT_REAL_ROUND_QUERY)
        round, = curs.fetchone()

    return round


def update_real_round_in_db(new_round: int):
    """Update real_round of global config stored in DB."""
    with storage.db_cursor() as (conn, curs):
        curs.execute(_UPDATE_REAL_ROUND_QUERY, (new_round,))
        conn.commit()


def set_game_running(new_value: bool):
    """Update game_running value in db."""
    with storage.db_cursor() as (conn, curs):
        curs.execute(_SET_GAME_RUNNING_QUERY, (new_value,))
        conn.commit()


def get_game_running() -> bool:
    """Get current game_running value from db."""
    with storage.db_cursor() as (_, curs):
        curs.execute(_GET_GAME_RUNNING_QUERY)
        game_running, = curs.fetchone()

    return game_running


def get_db_global_config() -> models.GlobalConfig:
    """Get global config from database."""
    with storage.db_cursor(dict_cursor=True) as (_, curs):
        curs.execute(_GET_GLOBAL_CONFIG_QUERY)
        result = curs.fetchone()

    return models.GlobalConfig.from_dict(result)


def get_current_global_config() -> models.GlobalConfig:
    """Get global config from cache is cached, cache it otherwise."""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cache_helper(
            pipeline=pipeline,
            cache_key='global_config',
            cache_func=storage.caching.cache_global_config,
            cache_args=(pipeline,),
        )

        result, = pipeline.get('global_config').execute()
        global_config = models.GlobalConfig.from_json(result)

    return global_config


async def global_config_async_getter(redis_aio, pipe):
    """Async version of get_current_global_config."""
    await async_cache_helper(
        redis_aio=redis_aio,
        cache_key='global_config',
        cache_func=caching.cache_global_config,
    )
    pipe.get('global_config')


def construct_game_state_from_db(current_round: int
                                 ) -> Optional[models.GameState]:
    """Get game state for specified round with teamtasks from db."""
    teamtasks = storage.tasks.get_teamtasks_from_db()
    teamtasks = storage.tasks.filter_teamtasks_for_participants(teamtasks)

    round_start = get_round_start(current_round)
    state = models.GameState(
        round_start=round_start,
        round=current_round,
        team_tasks=teamtasks,
    )
    return state


def construct_latest_game_state(current_round: int
                                ) -> Optional[models.GameState]:
    """Get game state from latest teamtasks from redis stream."""
    teamtasks = storage.tasks.get_last_teamtasks()
    teamtasks = storage.tasks.filter_teamtasks_for_participants(teamtasks)

    round_start = get_round_start(current_round)
    state = models.GameState(
        round_start=round_start,
        round=current_round,
        team_tasks=teamtasks,
    )
    return state


def game_state_getter(pipe):
    """Get game state for current round (asynchronous version)."""
    pipe.get('game_state')


async def get_attack_data(loop) -> str:
    """Get public flag ids for task that provide them."""
    redis_pool = await storage.get_async_redis_storage(loop)
    attack_data = await redis_pool.get('attack_data')
    return attack_data


def handle_attack(attacker_id: int,
                  flag_str: str,
                  current_round: int) -> models.AttackResult:
    """
    Main routine for attack validation & state change.

    Checks flag, locks team for update, calls rating recalculation,
    then publishes redis message about stolen flag

    :param attacker_id: id of the attacking team
    :param flag_str: flag to be checked
    :param current_round: round of the attack

    :return: attacker rating change
    """

    result = models.AttackResult(attacker_id=attacker_id)

    try:
        flag = storage.flags.get_flag_by_str(flag_str=flag_str,
                                             current_round=current_round)
        result.victim_id = flag.team_id
        result.task_id = flag.task_id
        storage.flags.try_add_stolen_flag(flag=flag, attacker=attacker_id,
                                          current_round=current_round)
        result.submit_ok = True

        with storage.db_cursor() as (conn, curs):
            curs.callproc(
                "recalculate_rating",
                (
                    attacker_id,
                    flag.team_id,
                    flag.task_id,
                    flag.id,
                ),
            )
            attacker_delta, victim_delta = curs.fetchone()
            conn.commit()

        result.attacker_delta = attacker_delta
        result.victim_delta = victim_delta
        result.message = f'Flag accepted! Earned {attacker_delta} flag points!'

        flag_data = {
            'attacker_id': attacker_id,
            'victim_id': flag.team_id,
            'task_id': flag.task_id,
            'attacker_delta': attacker_delta,
            'victim_delta': victim_delta,
        }

        storage.get_wro_sio_manager().emit(
            event='flag_stolen',
            data={'data': flag_data},
            namespace='/live_events',
        )

    except FlagSubmitException as e:
        result.message = str(e)

    return result


async def construct_scoreboard() -> dict:
    """
    Get formatted scoreboard to serve to frontend

    Fetches and constructs the full scoreboard (state, teams, tasks, config)
    using asyncio (for sanic webapi)
    """
    redis_aio = await storage.get_async_redis_storage()
    pipe = redis_aio.pipeline()
    pipe.get('game_state')
    await storage.teams.teams_async_getter(redis_aio, pipe)
    await storage.tasks.tasks_async_getter(redis_aio, pipe)
    await global_config_async_getter(redis_aio, pipe)
    state, teams, tasks, game_config = await pipe.execute()

    try:
        state = models.GameState.from_json(state).to_dict()
    except TypeError:
        state = None

    teams = [
        models.Team.from_json(team).to_dict_for_participants()
        for team in teams
    ]
    tasks = [
        models.Task.from_json(task).to_dict_for_participants()
        for task in tasks
    ]
    game_config = models.GlobalConfig.from_json(game_config).to_dict()

    data = {
        'state': state,
        'teams': teams,
        'tasks': tasks,
        'config': game_config,
    }

    return data
