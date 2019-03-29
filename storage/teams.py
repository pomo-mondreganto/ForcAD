from typing import List

import storage
from helpers import models
from storage import caching


def get_teams() -> List[models.Team]:
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        cached, = pipeline.exists('teams:cached').execute()
        if not cached:
            caching.cache_teams()

        teams, = pipeline.smembers('teams').execute()
        teams = list(models.Team.from_json(team) for team in teams)

    return teams
