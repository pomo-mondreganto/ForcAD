import time
from typing import Optional

from kombu.utils import json as kjson

from lib import models, storage
from lib.helpers.cache import cache_helper
from lib.storage import caching, utils
from lib.storage.keys import CacheKeys

_CURRENT_REAL_ROUND_QUERY = 'SELECT real_round FROM GameConfig WHERE id=1'

_UPDATE_REAL_ROUND_QUERY = 'UPDATE GameConfig SET real_round = %(round)s WHERE id=1'

_SET_GAME_RUNNING_QUERY = 'UPDATE GameConfig SET game_running = %(value)s WHERE id=1'

_GET_GAME_RUNNING_QUERY = 'SELECT game_running FROM GameConfig WHERE id=1'

_GET_GAME_CONFIG_QUERY = 'SELECT * FROM GameConfig WHERE id=1'


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
    """Update real_round of game config stored in DB."""
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


def get_db_game_config() -> models.GameConfig:
    """Get game config from database."""
    with utils.db_cursor(dict_cursor=True) as (_, curs):
        curs.execute(_GET_GAME_CONFIG_QUERY)
        result = curs.fetchone()

    return models.GameConfig.from_dict(result)


def get_current_game_config() -> models.GameConfig:
    """Get game config from cache is cached, cache it otherwise."""
    with utils.redis_pipeline(transaction=True) as pipe:
        cache_helper(
            pipeline=pipe,
            cache_key=CacheKeys.game_config(),
            cache_func=caching.cache_game_config,
            cache_args=(pipe,),
        )

        result, = pipe.get(CacheKeys.game_config()).execute()

    game_config = models.GameConfig.from_json(result)
    return game_config


def construct_game_state_from_db(current_round: int) -> models.GameState:
    """Get game state for specified round with teamtasks from db."""
    teamtasks = storage.tasks.get_teamtasks_from_db()
    teamtasks = storage.tasks.filter_teamtasks_for_participants(teamtasks)

    team_ids = {team.id for team in storage.teams.get_teams()}
    task_ids = {task.id for task in storage.tasks.get_tasks()}

    teamtasks = list(filter(
        lambda tt: tt['team_id'] in team_ids and tt['task_id'] in task_ids,
        teamtasks,
    ))

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


def get_cached_game_state() -> Optional[models.GameState]:
    with storage.utils.redis_pipeline(transaction=False) as pipe:
        state, = pipe.get(CacheKeys.game_state()).execute()

    if not state:
        return None
    return models.GameState.from_json(state)


def construct_scoreboard() -> dict:
    """
    Get formatted scoreboard to serve to frontend.
    Fetches and constructs the full scoreboard (state, teams, tasks, config).
    """

    teams = [team.to_dict_for_participants() for team in storage.teams.get_teams()]
    tasks = [task.to_dict_for_participants() for task in storage.tasks.get_tasks()]
    cfg = storage.game.get_current_game_config().to_dict()

    state = get_cached_game_state()
    if state:
        state = state.to_dict()

    data = {
        'state': state,
        'teams': teams,
        'tasks': tasks,
        'config': cfg,
    }

    return data


def construct_ctftime_scoreboard() -> Optional[list]:
    game_state = get_cached_game_state()

    if not game_state:
        return None

    teams = storage.teams.get_teams()

    standings = []
    for team in teams:
        team_id = team.id
        teamtasks = list(filter(
            lambda x: x['team_id'] == team_id,
            game_state.team_tasks,
        ))

        score = sum(map(
            lambda x: x['score'] * x['checks_passed'] / x['checks'],
            teamtasks,
        ))
        score = round(score, 2)
        standings.append({'team': team.name, 'score': score})

    standings = sorted(standings, key=lambda x: x['score'], reverse=True)
    standings = [
        {'pos': i + 1, **data}
        for i, data in enumerate(standings)
    ]
    return standings


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


def update_game_state(for_round: int) -> models.GameState:
    game_state = storage.game.construct_game_state_from_db(for_round)
    with utils.redis_pipeline(transaction=True) as pipe:
        pipe.set(storage.keys.CacheKeys.game_state(), game_state.to_json())
        pipe.execute()

    utils.SIOManager.write_only().emit(
        event='update_scoreboard',
        data={'data': game_state.to_dict()},
        namespace='/game_events',
    )

    return game_state
