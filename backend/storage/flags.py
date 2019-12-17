import secrets

import redis
from typing import Optional

import config
import helplib
import storage
from storage import caching

_INSERT_STOLEN_FLAG_QUERY = "INSERT INTO stolenflags (attacker_id, flag_id) VALUES (%s, %s)"

_INCREMENT_LOST_FLAGS_QUERY = "UPDATE teamtasks SET lost = lost + 1 WHERE team_id=%s AND task_id = %s"

_INCREMENT_STOLEN_FLAGS_QUERY = "UPDATE teamtasks SET stolen = stolen + 1 WHERE team_id=%s AND task_id=%s"

_INSERT_FLAG_QUERY = """
INSERT INTO flags (flag, team_id, task_id, round, flag_data, vuln_number) 
VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
"""


def add_stolen_flag(flag: helplib.models.Flag, attacker: int):
    """Add stolen flag both to database and cache

        :param flag: Flag model instance
        :param attacker: team id for the attacking team

        Using this function implies that the flag is validated,
        as it doesn't check anything
    """
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        pipeline.sadd(f'team:{attacker}:stolen_flags', flag.id)
        pipeline.incr(f'team:{attacker}:task:{flag.task_id}:stolen')
        pipeline.incr(f'team:{flag.team_id}:task:{flag.task_id}:lost')
        pipeline.execute()

    with storage.db_cursor() as (conn, curs):
        curs.execute(_INSERT_STOLEN_FLAG_QUERY, (attacker, flag.id))
        curs.execute(_INCREMENT_LOST_FLAGS_QUERY, (flag.team_id, flag.task_id))
        curs.execute(_INCREMENT_STOLEN_FLAGS_QUERY, (attacker, flag.task_id))

        conn.commit()


def check_flag(flag: helplib.models.Flag, attacker: int, round: int):
    """Check that flag is valid for current round

        :param flag: Flag model instance
        :param attacker: attacker team id
        :param round: current round

        :raises: an instance of FlagSubmitException on validation error
    """
    game_config = config.get_global_config()

    if round - flag.round > game_config['flag_lifetime']:
        raise helplib.exceptions.FlagSubmitException('Flag is too old')

    if flag.team_id == attacker:
        raise helplib.exceptions.FlagSubmitException('Flag is your own')

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached_stolen, cached_owned = pipeline.exists(
            f'team:{attacker}:cached:stolen',
        ).exists(
            f'team:{flag.team_id}:cached:owned',
        ).execute()

        if not cached_stolen or not cached_owned:
            while True:
                try:
                    pipeline.watch(
                        f'team:{attacker}:cached:stolen',
                        f'team:{flag.team_id}:cached:owned',
                    )

                    cached_stolen = pipeline.exists(f'team:{attacker}:cached:stolen')
                    cached_owned = pipeline.exists(f'team:{flag.team_id}:cached:owned')

                    pipeline.multi()

                    if not cached_stolen:
                        caching.cache_last_stolen(attacker, round, pipeline)

                    if not cached_owned:
                        caching.cache_last_owned(flag.team_id, round, pipeline)

                    pipeline.execute()
                    break
                except redis.WatchError:
                    continue

        pipeline.sismember(f'team:{flag.team_id}:owned_flags', flag.id)
        pipeline.sismember(f'team:{attacker}:stolen_flags', flag.id)

        is_owned, is_stolen = pipeline.execute()

        if not is_owned:
            raise helplib.exceptions.FlagSubmitException('Flag is invalid or too old')

        if is_stolen:
            raise helplib.exceptions.FlagSubmitException('Flag already stolen')


def add_flag(flag: helplib.models.Flag) -> helplib.models.Flag:
    """Inserts a newly generated flag into the database and cache

        :param flag: Flag model instance to be inserted
        :return: flag with set "id" field
    """

    with storage.db_cursor() as (conn, curs):
        curs.execute(
            _INSERT_FLAG_QUERY,
            (
                flag.flag,
                flag.team_id,
                flag.task_id,
                flag.round,
                flag.flag_data,
                flag.vuln_number,
            )
        )
        flag.id, = curs.fetchone()
        conn.commit()

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        while True:
            try:
                pipeline.watch(f'team:{flag.team_id}:cached:owned')
                cached = pipeline.exists(f'team:{flag.team_id}:cached:owned')

                pipeline.multi()

                if not cached:
                    caching.cache_last_owned(flag.team_id, flag.round, pipeline)
                else:
                    pipeline.sadd(f'team:{flag.team_id}:owned_flags', flag.id)

                pipeline.execute()
                break
            except redis.WatchError:
                continue

        pipeline.sadd(f'team:{flag.team_id}:task:{flag.task_id}:round_flags:{flag.round}', flag.id)
        pipeline.set(f'flag:id:{flag.id}', flag.to_json())
        pipeline.set(f'flag:str:{flag.flag}', flag.to_json())
        pipeline.execute()

    return flag


def get_flag_by_field(field_name: str, field_value, round: int) -> helplib.models.Flag:
    """Get flag by generic field

        :param field_name: field name to ask cache for
        :param field_value: value of the field "field_name" to filter on
        :param round: current round
        :return: Flag model instance with flag.field_name == field_value
        :raises: FlagSubmitException if nothing found
    """
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('flags:cached').execute()
        if not cached:
            while True:
                try:
                    pipeline.watch('flags:cached')
                    cached = pipeline.exists('flags:cached')

                    pipeline.multi()

                    if not cached:
                        caching.cache_last_flags(round, pipeline)

                    pipeline.execute()
                    break
                except redis.WatchError:
                    continue

        pipeline.exists(f'flag:{field_name}:{field_value}')
        pipeline.get(f'flag:{field_name}:{field_value}')
        flag_exists, flag_json = pipeline.execute()

    if not flag_exists:
        raise helplib.exceptions.FlagSubmitException('Invalid flag')

    flag = helplib.models.Flag.from_json(flag_json)

    return flag


def get_flag_by_str(flag_str: str, round: int) -> helplib.models.Flag:
    """Get flag by its string value

        :param flag_str: flag value
        :param round: current round
        :return: Flag model instance
    """
    return get_flag_by_field(field_name='str', field_value=flag_str, round=round)


def get_flag_by_id(flag_id: int, round: int) -> helplib.models.Flag:
    """Get flag by its id value

            :param flag_id: flag id
            :param round: current round
            :return: Flag model instance
    """
    return get_flag_by_field(field_name='id', field_value=flag_id, round=round)


def get_random_round_flag(team_id: int, task_id: int, round: int, current_round: int) -> Optional[helplib.models.Flag]:
    """Get random flag for team generated for specified round and task

        :param team_id: team id
        :param task_id: task id
        :param round: round to fetch flag for
        :param current_round: current round
        :return: Flag mode instance or None if no flag from rounds exist
    """

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('flags:cached').execute()
        if not cached:
            while True:
                try:
                    pipeline.watch('flags:cached')
                    cached = pipeline.exists('flags:cached')

                    pipeline.multi()

                    if not cached:
                        caching.cache_last_flags(current_round, pipeline)

                    pipeline.execute()
                    break
                except redis.WatchError:
                    continue

        flags, = pipeline.smembers(f'team:{team_id}:task:{task_id}:round_flags:{round}').execute()
        try:
            flag_id = int(secrets.choice(list(flags)).decode())
        except (ValueError, IndexError, AttributeError):
            return None
    return get_flag_by_id(flag_id, current_round)
