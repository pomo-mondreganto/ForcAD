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
INITIALIZER_CONTAINER_NAME = 'forcad_initializer_1'


def wait_for_container(name):
    command = ['docker', 'wait', name]
    result = int(subprocess.check_output(command).decode().strip())
    if result != 0:
        print(f'Error in container {name}')
        p = subprocess.Popen(['docker-compose', 'logs'], cwd=PROJECT_DIR)
        p.wait()
        sys.exit(1)


def wait_all():
    wait_for_container(INITIALIZER_CONTAINER_NAME)
    wait_rounds(3)


if __name__ == '__main__':
    wait_all()
