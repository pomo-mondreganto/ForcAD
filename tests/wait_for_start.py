import os

import subprocess
import time
import yaml

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_DIR, 'backend')

DOCKER_COMPOSE_FILE = 'docker-compose-tests.yml'
INITIALIZER_CONTAINER_NAME = 'forcad_initializer_1'
FRONT_BUILD_CONTAINER_NAME = 'forcad_front_builder_1'


def wait_for_container(name):
    command = ['docker', 'wait', name]
    result = int(subprocess.check_output(command).decode().strip())
    if result != 0:
        print(f'Error in container {name}')
        p = subprocess.Popen(['docker-compose', 'logs'], cwd=PROJECT_DIR)
        p.wait()
        exit(1)


def wait_rounds(rounds):
    conf_path = os.path.join(BACKEND_DIR, 'config/test_config.yml')
    with open(conf_path) as f:
        main_config = yaml.load(f, Loader=yaml.FullLoader)

    round_time = main_config['global']['round_time']
    time.sleep(rounds * round_time)


def wait_all():
    wait_for_container(INITIALIZER_CONTAINER_NAME)
    wait_for_container(FRONT_BUILD_CONTAINER_NAME)
    wait_rounds(2)


if __name__ == '__main__':
    wait_all()
