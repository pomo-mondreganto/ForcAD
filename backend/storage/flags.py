import secrets
from collections import defaultdict

from typing import Optional, List, Dict

import helplib
import storage
from helplib.cache import cache_helper
from storage import caching

_INSERT_FLAG_QUERY = """
INSERT INTO flags (flag, team_id, task_id, round, public_flag_data, private_flag_data, vuln_number) 
VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
"""

_GET_UNEXPIRED_FLAGS_QUERY = """
SELECT t.ip, f.task_id, f.public_flag_data FROM flags f
INNER JOIN teams t on f.team_id = t.id
WHERE f.round >= %s AND f.task_id IN %s
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
        # optimization of redis request count
        cached_stolen = pipeline.exists(f'team:{attacker}:stolen_flags:cached').execute()

        if not cached_stolen:
            cache_helper(
                pipeline=pipeline,
                cache_key=f'team:{attacker}:stolen_flags:cached',
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
                flag.public_flag_data,
                flag.private_flag_data,
                flag.vuln_number,
            )
        )
        flag.id, = curs.fetchone()
        conn.commit()

    game_config = storage.game.get_current_global_config()
    expires = game_config.flag_lifetime * game_config.round_time * 2  # can be smaller

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        round_flags_key = f'team:{flag.team_id}:task:{flag.task_id}:round_flags:{flag.round}'
        pipeline.sadd(round_flags_key, flag.id)
        pipeline.expire(round_flags_key, expires)

        pipeline.set(f'flag:id:{flag.id}', flag.to_json(), ex=expires)
        pipeline.set(f'flag:str:{flag.flag}', flag.to_json(), ex=expires)
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
        raise helplib.exceptions.FlagSubmitException('Flag is invalid or too old')

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
        cache_helper(
            pipeline=pipeline,
            cache_key='flags:cached',
            cache_func=caching.cache_last_flags,
            cache_args=(current_round, pipeline),
        )

        flags, = pipeline.smembers(f'team:{team_id}:task:{task_id}:round_flags:{round}').execute()
        try:
            flag_id = int(secrets.choice(list(flags)))
        except (ValueError, IndexError, TypeError):
            return None
    return get_flag_by_id(flag_id, current_round)


def get_attack_data(current_round: int, tasks: List[helplib.models.Task]) -> Dict[str, Dict[int, List[str]]]:
    """Get unexpired flags for round in format {task.name: {team.ip: [flag.public_data]}}"""
    task_ids = tuple(task.id for task in tasks)
    task_names = {task.id: task.name for task in tasks}

    config = storage.game.get_current_global_config()
    need_round = current_round - config.flag_lifetime

    if task_ids:
        with storage.db_cursor() as (conn, curs):
            curs.execute(
                _GET_UNEXPIRED_FLAGS_QUERY,
                (need_round, task_ids)
            )
            flags = curs.fetchall()
    else:
        flags = []

    data = {task_names[task_id]: defaultdict(list) for task_id in task_ids}
    for flag in flags:
        ip, task_id, flag_data = flag
        data[task_names[task_id]][ip].append(flag_data)

    return data
