import subprocess
import sys

from pathlib import Path

PROJECT_DIR = Path(__file__).absolute().resolve().parents[1]
BACKEND_DIR = PROJECT_DIR / 'backend'
TESTS_DIR = PROJECT_DIR / 'tests'
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(TESTS_DIR))

from helpers import wait_rounds

DOCKER_COMPOSE_FILE = 'docker-compose-tests.yml'
INITIALIZER_CONTAINER_NAME = 'forcad-initializer-1'
INITIALIZER_CONTAINER_NAME_OLD = 'forcad_initializer_1'


def wait_for_initializer():
    # Docker Compose broke compatibility in container naming.
    out = subprocess.check_output(['docker', 'ps', '-a']).decode()
    if INITIALIZER_CONTAINER_NAME in out:
        name = INITIALIZER_CONTAINER_NAME
    else:
        name = INITIALIZER_CONTAINER_NAME_OLD

    print(f'Waiting for container {name}')
    command = ['docker', 'wait', name]
    result = int(subprocess.check_output(command).decode().strip())
    if result != 0:
        print(f'Error in container {name}')
        subprocess.run(['docker', 'compose', 'logs'], cwd=PROJECT_DIR)
        sys.exit(1)


def wait_all():
    wait_for_initializer()
    wait_rounds(3)


if __name__ == '__main__':
    wait_all()
    print('ForcAD started!')
