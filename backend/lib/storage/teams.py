from typing import List, Optional

from lib import models
from lib import storage
from lib.helpers.cache import cache_helper


def get_teams() -> List[models.Team]:
    """Get list of teams registered in the database."""
    with storage.utils.get_redis_storage().pipeline(transaction=True) as pipe:
        cache_helper(
            pipeline=pipe,
            cache_key='teams',
            cache_func=storage.caching.cache_teams,
            cache_args=(pipe,),
        )

        teams, = pipe.smembers('teams').execute()
        teams = list(models.Team.from_json(team) for team in teams)

    return teams


def get_team_id_by_token(token: str) -> Optional[int]:
    """
    Get team by token.

    :param token: token string
    :return: team id
    """
    with storage.utils.get_redis_storage().pipeline(transaction=False) as pipe:
        team_id, = pipe.get(f'team:token:{token}').execute()

    try:
        team_id = int(team_id)
    except (ValueError, TypeError):
        return None
    else:
        return team_id


def flush_teams_cache():
    with storage.utils.get_redis_storage().pipeline(transaction=False) as pipe:
        pipe.delete('teams').execute()


def create_team(team: models.Team) -> models.Team:
    """Add new team to DB, reset cache & return created instance."""
    with storage.utils.db_cursor() as (conn, curs):
        curs.execute(team.get_insert_query(), team.to_dict())
        result, = curs.fetchone()
        team.id = result

        insert_data = [
            (task.id, team.id, task.default_score, -1)
            for task in storage.tasks.get_tasks()
        ]
        for each in insert_data:
            curs.execute(storage.tasks.TEAMTASK_INSERT_QUERY, each)

        conn.commit()

    flush_teams_cache()
    return team


def update_team(team: models.Team) -> models.Team:
    """Update team, reset cache & return updated instance."""
    with storage.utils.db_cursor() as (conn, curs):
        curs.execute(team.get_update_query(), team.to_dict())
        conn.commit()

    flush_teams_cache()
    return team


def delete_team(team_id: int) -> None:
    """Set active = False on a team."""
    with storage.utils.db_cursor() as (conn, curs):
        curs.execute(models.Team.get_delete_query(), {'id': team_id})
        conn.commit()

    flush_teams_cache()
