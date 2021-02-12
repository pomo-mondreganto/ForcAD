import time
from typing import Optional

from kombu.utils import json as kjson

from lib import models, storage
from lib.helpers.cache import cache_helper
from lib.storage import caching, utils
from lib.storage.keys import CacheKeys

_CURRENT_REAL_ROUND_QUERY = 'SELECT real_round FROM globalconfig WHERE id=1'

_UPDATE_REAL_ROUND_QUERY = 'UPDATE globalconfig SET real_round = %(round)s WHERE id=1'

_SET_GAME_RUNNING_QUERY = 'UPDATE globalconfig SET game_running = %(value)s WHERE id=1'

_GET_GAME_RUNNING_QUERY = 'SELECT game_running FROM globalconfig WHERE id=1'

_GET_GLOBAL_CONFIG_QUERY = 'SELECT * FROM globalconfig WHERE id=1'


def get_round_start(r: int) -> int:
    """Get start time for round as unix timestamp."""
    with utils.redis_pipeline(transaction=False) as pipe:
        start_time, = pipe.get(CacheKeys.round_start(r)).execute()
    return int(start_time or 0)


def set_round_start(r: int) -> None:
    """Set start time for round as str."""
    cur_time = int(time.time())
    with utils.redis_pipeline(transaction=False) as pipe:
        pipe.set(CacheKeys.round_start(r), cur_time).execute()


def get_real_round() -> int:
    """
    Get real round of system (for flag submitting).

    :returns: -1 if round not in cache, else round
    """
    with utils.redis_pipeline(transaction=False) as pipe:
        r, = pipe.get(CacheKeys.current_round()).execute()

    return int(r or -1)


def get_real_round_from_db() -> int:
    """Get real round from database. Fully persistent to use with game management."""
    with utils.db_cursor() as (_, curs):
        curs.execute(_CURRENT_REAL_ROUND_QUERY)
        r, = curs.fetchone()

    return r


def update_real_round_in_db(new_round: int) -> None:
    """Update real_round of global config stored in DB."""
    with utils.db_cursor() as (conn, curs):
        curs.execute(_UPDATE_REAL_ROUND_QUERY, {'round': new_round})
        conn.commit()


def set_game_running(new_value: bool) -> None:
    """Update game_running value in db."""
    with utils.db_cursor() as (conn, curs):
        curs.execute(_SET_GAME_RUNNING_QUERY, {'value': new_value})
        conn.commit()


def get_game_running() -> bool:
    """Get current game_running value from db."""
    with utils.db_cursor() as (_, curs):
        curs.execute(_GET_GAME_RUNNING_QUERY)
        game_running, = curs.fetchone()

    return game_running


def get_db_global_config() -> models.GlobalConfig:
    """Get global config from database."""
    with utils.db_cursor(dict_cursor=True) as (_, curs):
        curs.execute(_GET_GLOBAL_CONFIG_QUERY)
        result = curs.fetchone()

    return models.GlobalConfig.from_dict(result)


def get_current_global_config() -> models.GlobalConfig:
    """Get global config from cache is cached, cache it otherwise."""
    with utils.redis_pipeline(transaction=True) as pipe:
        cache_helper(
            pipeline=pipe,
            cache_key=CacheKeys.global_config(),
            cache_func=caching.cache_global_config,
            cache_args=(pipe,),
        )

        result, = pipe.get(CacheKeys.global_config()).execute()
        global_config = models.GlobalConfig.from_json(result)

    return global_config


def construct_game_state_from_db(current_round: int) -> Optional[models.GameState]:
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


def construct_latest_game_state(current_round: int) -> models.GameState:
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


def construct_scoreboard() -> dict:
    """
    Get formatted scoreboard to serve to frontend.
    Fetches and constructs the full scoreboard (state, teams, tasks, config).
    """

    teams = [team.to_dict_for_participants() for team in storage.teams.get_teams()]
    tasks = [task.to_dict_for_participants() for task in storage.tasks.get_tasks()]
    cfg = storage.game.get_current_global_config().to_dict()

    with storage.utils.redis_pipeline(transaction=False) as pipe:
        state, = pipe.get(CacheKeys.game_state()).execute()

    try:
        state = models.GameState.from_json(state).to_dict()
    except TypeError:
        state = None

    data = {
        'state': state,
        'teams': teams,
        'tasks': tasks,
        'config': cfg,
    }

    return data


def update_round(finished_round: int) -> None:
    new_round = finished_round + 1

    set_round_start(r=new_round)
    update_real_round_in_db(new_round=new_round)

    with utils.redis_pipeline(transaction=False) as pipe:
        pipe.set(CacheKeys.current_round(), new_round)
        pipe.execute()


def update_attack_data(current_round: int) -> None:
    tasks = storage.tasks.get_tasks()
    tasks = list(filter(lambda x: x.checker_provides_public_flag_data, tasks))
    attack_data = storage.flags.get_attack_data(current_round, tasks)
    with utils.redis_pipeline(transaction=False) as pipe:
        pipe.set(CacheKeys.attack_data(), kjson.dumps(attack_data))
        pipe.execute()
