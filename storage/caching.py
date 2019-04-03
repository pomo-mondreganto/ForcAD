from psycopg2 import extras

import config
import helpers.models
import storage
from helpers import models


def cache_teams():
    query = 'SELECT * from teams'

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor(cursor_factory=extras.DictCursor)
    curs.execute(query)

    teams = curs.fetchall()
    teams = list(models.Team.from_dict(team) for team in teams)

    storage.get_db_pool().putconn(conn)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete('teams', 'teams:cached')
        for team in teams:
            pipeline.sadd('teams', team.to_json())
            pipeline.set(f'team:token:{team.token}', team.id)
        pipeline.set('teams:cached', 1)
        pipeline.execute()


def cache_tasks():
    query = 'SELECT * from tasks'

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor(cursor_factory=extras.DictCursor)
    curs.execute(query)

    tasks = curs.fetchall()
    tasks = list(models.Task.from_dict(task) for task in tasks)

    storage.get_db_pool().putconn(conn)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete('tasks', 'tasks:cached')
        for task in tasks:
            pipeline.sadd('tasks', task.to_json())
        pipeline.set('tasks:cached', 1)
        pipeline.execute()


def cache_last_stolen(team_id: int, round: int):
    game_config = config.get_game_config()
    query = (
        "SELECT S.flag_id from stolenflags S "
        "INNER JOIN flags F ON F.id = S.flag_id "
        "WHERE F.round >= %s and S.attacker_id = %s"
    )

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()
    curs.execute(query, (round - game_config['flag_lifetime'], team_id))
    flags = curs.fetchall()

    storage.get_db_pool().putconn(conn)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete(f'team_{team_id}:cached_stolen', f'team_{team_id}:stolen_flags')
        for flag_id, in flags:
            pipeline.sadd(f'team_{team_id}:stolen_flags', flag_id)
        pipeline.set(f'team_{team_id}:cached_stolen', 1)
        pipeline.execute()


def cache_last_owned(team_id: int, round: int):
    game_config = config.get_game_config()
    query = (
        "SELECT id from flags WHERE round >= %s AND team_id = %s"
    )

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()
    curs.execute(query, (round - game_config['flag_lifetime'], team_id))
    flags = curs.fetchall()

    storage.get_db_pool().putconn(conn)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete(f'team_{team_id}:owned_flags', f'team_{team_id}:cached_owned')
        for flag_id, in flags:
            pipeline.sadd(f'team_{team_id}:owned_flags', flag_id)
        pipeline.set(f'team_{team_id}:cached_owned', 1)
        pipeline.execute()


def cache_last_flags(round: int):
    game_config = config.get_game_config()
    query = (
        "SELECT * from flags WHERE round >= %s"
    )

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor(cursor_factory=extras.DictCursor)

    curs.execute(query, (round - game_config['flag_lifetime'],))
    flags = curs.fetchall()

    storage.get_db_pool().putconn(conn)

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.delete('cached_flags')
        rflags = []
        for flag_d in flags:
            flag = helpers.models.Flag.from_dict(flag_d)
            rflags.append(flag)
            pipeline.delete(f'team:{flag.team_id}:task:{flag.task_id}:round_flags:{flag.round}')
        for flag in rflags:
            pipeline.set(f'flag_id:{flag.id}', flag.to_json())
            pipeline.set(f'flag_str:{flag.flag}', flag.to_json())
            pipeline.sadd(f'team:{flag.team_id}:task:{flag.task_id}:round_flags:{flag.round}', flag.id)

        pipeline.set(f'cached_flags', 1)
        pipeline.execute()
