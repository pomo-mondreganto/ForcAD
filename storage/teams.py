from typing import List

import storage
from helpers import models
from storage import caching


def get_teams() -> List[models.Team]:
    """Get list of teams registered in the database"""
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('teams:cached').execute()
        if not cached:
            caching.cache_teams()

        teams, = pipeline.smembers('teams').execute()
        teams = list(models.Team.from_json(team) for team in teams)

    return teams


def get_team_id_by_token(token: str) -> int:
    """Get team by token

        :param token: token string
        :return: team id
    """
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('teams:cached').execute()
        if not cached:
            caching.cache_teams()

        team_id, = pipeline.get(f'team:token:{token}').execute()

    return team_id
