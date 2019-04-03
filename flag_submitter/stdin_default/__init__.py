import sys

import storage
from helpers import exceptions

print('Welcome! Please, enter your team token:')
token = input().strip()

team_id = storage.teams.get_team_id_by_token(token)

if not team_id:
    print('Invalid team token')
    sys.exit(0)

while True:
    flag_str = input().strip()

    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        round = pipeline.get('round')

    if not round:
        print('Game is unavailable yet')
        continue

    flag = storage.flags.get_flag_by_str(flag_str=flag_str, round=round)

    try:
        storage.flags.check_flag(flag=flag, attacker=team_id, round=round)
    except exceptions.FlagSubmitException as e:
        print(e)
        continue

    storage.flags.add_stolen_flag(flag=flag, attacker=team_id)
    # TODO: rating system, points

    print('Flag accepted!')
