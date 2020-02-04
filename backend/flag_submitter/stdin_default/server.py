import os

import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

import storage
from helplib import exceptions

print('Welcome! Please, enter your team token:')
token = input().strip()

team_id = storage.teams.get_team_id_by_token(token)

if not team_id:
    print('Invalid team token')
    sys.exit(0)

print('Now enter your flags, one in a line:')

flags_submitted = 0
flags_correct = 0
overall_time = 0.0

while True:
    try:
        flag_str = input().strip()
    except EOFError:
        break

    start_time = time.time()

    round = storage.game.get_real_round()

    if round == -1:
        print('Game is unavailable')

    try:
        attacker_delta = storage.teams.handle_attack(
            attacker_id=team_id,
            flag_str=flag_str,
            round=round,
        )
    except exceptions.FlagSubmitException as e:
        print(e)
    else:
        flags_correct += 1
        print(f'Flag accepted! Earned {attacker_delta} flag points!')

    flags_submitted += 1
    end_time = time.time()
    overall_time += end_time - start_time

average = overall_time / flags_submitted

print(f'Submitted a total of {flags_submitted} flags, {flags_correct} correct flags', file=sys.stderr)
print(
    f'Overall time processing flags is {overall_time:.5f} seconds, average is {average * 1000:.3f}ms per flag',
    file=sys.stderr,
)
