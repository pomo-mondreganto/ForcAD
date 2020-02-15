import secrets

from typing import Optional

import helplib
import storage
from helplib.cache import cache_helper
from storage import caching

_INSERT_FLAG_QUERY = """
INSERT INTO flags (flag, team_id, task_id, round, flag_data, vuln_number) 
VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
"""


def try_add_stolen_flag(flag: helplib.models.Flag, attacker: int, round: int):
    """Check that flag is valid for current round, add it to cache, then add to db

        :param flag: Flag model instance
        :param attacker: attacker team id
        :param round: current round

        :raises: an instance of FlagSubmitException on validation error
    """
    game_config = storage.game.get_current_global_config()
    if round - flag.round > game_config.flag_lifetime:
        raise helplib.exceptions.FlagSubmitException('Flag is too old')
    if flag.team_id == attacker:
        raise helplib.exceptions.FlagSubmitException('Flag is your own')

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached_stolen = pipeline.exists(f'team:{attacker}:cached:stolen').execute()

        if not cached_stolen:
            cache_helper(
                pipeline=pipeline,
                cache_key=f'team:{attacker}:cached:stolen',
                cache_func=caching.cache_last_stolen,
                cache_args=(attacker, round, pipeline),
            )

        is_new, = pipeline.sadd(f'team:{attacker}:stolen_flags', flag.id).execute()

        if not is_new:
            raise helplib.exceptions.FlagSubmitException('Flag already stolen')

        pipeline.incr(f'team:{attacker}:task:{flag.task_id}:stolen')
        pipeline.incr(f'team:{flag.team_id}:task:{flag.task_id}:lost')
        pipeline.execute()


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
        cache_helper(
            pipeline=pipeline,
            cache_key=f'team:{flag.team_id}:cached:owned',
            cache_func=caching.cache_last_owned,
            cache_args=(flag.team_id, flag.round, pipeline),
            on_cached=pipeline.sadd,
            on_cached_args=(f'team:{flag.team_id}:owned_flags', flag.id),
        )

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
            cache_helper(
                pipeline=pipeline,
                cache_key='flags:cached',
                cache_func=caching.cache_last_flags,
                cache_args=(round, pipeline),
            )

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
            cache_helper(
                pipeline=pipeline,
                cache_key='flags:cached',
                cache_func=caching.cache_last_flags,
                cache_args=(current_round, pipeline),
            )

        flags, = pipeline.smembers(f'team:{team_id}:task:{task_id}:round_flags:{round}').execute()
        try:
            flag_id = int(secrets.choice(list(flags)).decode())
        except (ValueError, IndexError, AttributeError):
            return None
    return get_flag_by_id(flag_id, current_round)
