import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import storage
import config
from scripts import reset_db, init_db
from backend.scripts import print_tokens


def run():
    shared_directory = config.get_game_config()['shared_directory']
    round_file_path = os.path.join(shared_directory, 'round')
    game_running_file_path = os.path.join(shared_directory, 'game_running')

    if not os.path.isabs(round_file_path):
        round_file_path = os.path.join(BASE_DIR, round_file_path)

    if not os.path.isabs(game_running_file_path):
        game_running_file_path = os.path.join(BASE_DIR, game_running_file_path)

    try:
        os.remove(round_file_path)
    except FileNotFoundError:
        print('Round file not found')
        pass

    try:
        os.remove(game_running_file_path)
    except FileNotFoundError:
        print('Game running file not found')
        pass

    reset_db.run()
    init_db.run()

    r = storage.get_redis_storage()
    r.flushall()

    print('New team tokens:')
    print_tokens.run()


if __name__ == '__main__':
    run()
