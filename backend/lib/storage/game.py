import time
from typing import Optional

from lib import models, storage
from lib.helpers.cache import cache_helper
from lib.storage import caching, utils

_CURRENT_REAL_ROUND_QUERY = 'SELECT real_round FROM globalconfig WHERE id=1'

_UPDATE_REAL_ROUND_QUERY = 'UPDATE globalconfig SET real_round = %s WHERE id=1'

_SET_GAME_RUNNING_QUERY = '''
UPDATE globalconfig SET game_running = %s WHERE id=1
'''

_GET_GAME_RUNNING_QUERY = 'SELECT game_running FROM globalconfig WHERE id=1'

_GET_GLOBAL_CONFIG_QUERY = 'SELECT * FROM globalconfig WHERE id=1'


def get_round_start(r: int) -> int:
    """Get start time for round as unix timestamp."""
    with utils.get_redis_storage().pipeline(transaction=False) as pipeline:
        start_time, = pipeline.get(f'round:{r}:start_time').execute()
    try:
        start_time = int(start_time)
    except (ValueError, TypeError):
        start_time = 0
    return start_time


def set_round_start(r: int) -> None:
    """Set start time for round as str."""
    cur_time = int(time.time())
    with utils.get_redis_storage().pipeline(transaction=False) as pipeline:
        pipeline.set(f'round:{r}:start_time', cur_time).execute()


def get_real_round() -> int:
    """
    Get real round of system (for flag submitting).

    :returns: -1 if round not in cache, else round
    """
    with utils.get_redis_storage().pipeline(transaction=False) as pipeline:
        r, = pipeline.get('real_round').execute()

    try:
        r = int(r)
    except (ValueError, TypeError):
        return -1
    return r


def get_real_round_from_db() -> int:
    """
    Get real round from database.

    Fully persistent to use with game management
    """
    with utils.db_cursor() as (_, curs):
        curs.execute(_CURRENT_REAL_ROUND_QUERY)
        r, = curs.fetchone()

    return r


def update_real_round_in_db(new_round: int) -> None:
    """Update real_round of global config stored in DB."""
    with utils.db_cursor() as (conn, curs):
        curs.execute(_UPDATE_REAL_ROUND_QUERY, (new_round,))
        conn.commit()


def set_game_running(new_value: bool) -> None:
    """Update game_running value in db."""
    with utils.db_cursor() as (conn, curs):
        curs.execute(_SET_GAME_RUNNING_QUERY, (new_value,))
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
    with utils.get_redis_storage().pipeline(transaction=True) as pipeline:
        cache_helper(
            pipeline=pipeline,
            cache_key='global_config',
            cache_func=caching.cache_global_config,
            cache_args=(pipeline,),
        )

        result, = pipeline.get('global_config').execute()
        global_config = models.GlobalConfig.from_json(result)

    return global_config


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

    teams = [
        team.to_dict_for_participants()
        for team in storage.teams.get_teams()
    ]
    tasks = [
        task.to_dict_for_participants()
        for task in storage.tasks.get_tasks()
    ]
    cfg = storage.game.get_current_global_config().to_dict()

    with storage.utils.get_redis_storage().pipeline(transaction=False) as pipe:
        state, = pipe.get('game_state').execute()

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
