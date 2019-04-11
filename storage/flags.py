import secrets

import redis

import config
import helpers.exceptions
import storage
from helpers import models
from storage import caching


def add_stolen_flag(flag: helpers.models.Flag, attacker: int):
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.sadd(f'team:{attacker}:stolen_flags', flag.id)
        pipeline.incr(f'team:{attacker}:task:{flag.task_id}:stolen')
        pipeline.incr(f'team:{flag.team_id}:task:{flag.task_id}:lost')

    conn = storage.get_db_pool().getconn()
    curs = conn.cursor()

    query = "INSERT INTO stolenflags (attacker_id, flag_id) VALUES (%s, %s)"
    curs.execute(query, (attacker, flag.id))

    query = "UPDATE teamtasks SET lost = lost + 1 WHERE team_id=%s"
    curs.execute(query, (flag.team_id,))

    query = "UPDATE teamtasks SET stolen = stolen + 1 WHERE team_id=%s"
    curs.execute(query, (attacker,))

    conn.commit()
    storage.get_db_pool().putconn(conn)


def check_flag(flag: helpers.models.Flag, attacker: int, round: int):
    game_config = config.get_game_config()

    if round - flag.round > game_config['flag_lifetime']:
        raise helpers.exceptions.FlagSubmitException('Flag is too old')

    if flag.team_id == attacker:
        raise helpers.exceptions.FlagSubmitException('Flag is your own')

    pipeline = storage.get_redis_storage().pipeline(transaction=True)
    while True:
        try:
            pipeline.watch(
                f'team:{attacker}:stolen_flags',
                f'team:{attacker}:cached:stolen',
                f'team:{flag.team_id}:cached:owned',
            )

            cached_stolen = pipeline.exists(f'team:{attacker}:cached:stolen')
            cached_owned = pipeline.exists(f'team:{flag.team_id}:cached:owned')

            if not cached_stolen:
                caching.cache_last_stolen(attacker, round)

            if not cached_owned:
                caching.cache_last_owned(flag.team_id, round)

            is_owned = pipeline.sismember(f'team:{flag.team_id}:owned_flags', flag.id)
            is_stolen = pipeline.sismember(f'team:{attacker}:stolen_flags', flag.id)

            if not is_owned:
                raise helpers.exceptions.FlagSubmitException('Flag is invalid or too old')

            if is_stolen:
                raise helpers.exceptions.FlagSubmitException('Flag already stolen')

            break
        except redis.WatchError:
            continue
        finally:
            pipeline.reset()


def add_flag(flag: helpers.models.Flag) -> helpers.models.Flag:
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        query = "INSERT INTO flags (flag, team_id, task_id, round, flag_data) VALUES (%s, %s, %s, %s, %s) RETURNING id"

        conn = storage.get_db_pool().getconn()
        curs = conn.cursor()
        curs.execute(query, (flag.flag, flag.team_id, flag.task_id, flag.round, flag.flag_data))
        flag.id, = curs.fetchone()
        conn.commit()
        storage.get_db_pool().putconn(conn)

        cached, = pipeline.exists(f'team:{flag.team_id}:cached:owned').execute()
        if not cached:
            caching.cache_last_owned(flag.team_id, flag.round)
        else:
            pipeline.sadd(f'team:{flag.team_id}:owned_flags', flag.id)

        pipeline.sadd(f'team:{flag.team_id}:task:{flag.task_id}:round_flags:{flag.round}', flag.id)
        pipeline.set(f'flag:id:{flag.id}', flag.to_json())
        pipeline.set(f'flag:str:{flag.flag}', flag.to_json())
        pipeline.execute()

    return flag


def get_flag_by_field(field_name: str, field_value, round: int) -> helpers.models.Flag:
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('flags:cached').execute()
        if not cached:
            caching.cache_last_flags(round)

        pipeline.exists(f'flag:{field_name}:{field_value}')
        pipeline.get(f'flag:{field_name}:{field_value}')
        flag_exists, flag_json = pipeline.execute()

        if not flag_exists:
            raise helpers.exceptions.FlagSubmitException('Invalid flag')

        flag = helpers.models.Flag.from_json(flag_json)

    return flag


def get_flag_by_str(flag_str: str, round: int) -> helpers.models.Flag:
    return get_flag_by_field(field_name='str', field_value=flag_str, round=round)


def get_flag_by_id(flag_id: int, round: int) -> helpers.models.Flag:
    return get_flag_by_field(field_name='id', field_value=flag_id, round=round)


def get_random_round_flag(team_id: int, task_id: int, round: int, current_round: int) -> helpers.models.Flag:
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('cached:flags').execute()
        if not cached:
            caching.cache_last_flags(current_round)

        flags, = pipeline.smembers(f'team:{team_id}:task:{task_id}:round_flags:{round}').execute()
        flag_id = int(secrets.choice(list(flags)).decode())
        return get_flag_by_id(flag_id, current_round)
