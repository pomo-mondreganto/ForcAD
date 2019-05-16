"""STDIN flag submitter"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

import storage
import helpers
from helpers import exceptions

print('Welcome! Please, enter your team token:')
token = input().strip()

team_id = storage.teams.get_team_id_by_token(token)

if not team_id:
    print('Invalid team token')
    sys.exit(0)

print('Now enter your flags, one in a line:')

while True:
    flag_str = input().strip()

    round = storage.game.get_real_round()

    if round == -1:
        print('Game is unavailable yet')

    try:
        flag = helpers.flags.check_flag(flag_str=flag_str, attacker=team_id, round=round)
    except exceptions.FlagSubmitException as e:
        print(e)
        continue
    else:
        storage.flags.add_stolen_flag(flag=flag, attacker=team_id)
        attacker_delta = storage.teams.handle_attack(
            attacker_id=team_id,
            victim_id=flag.team_id,
            task_id=flag.task_id,
            round=round,
        )

        print(f'Flag accepted! Earned {attacker_delta} flag points!')
