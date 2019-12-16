import os
import subprocess

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCKER_COMPOSE_FILE = 'docker-compose-tests.yml'
INITIALIZER_CONTAINER_NAME = 'forcad_initializer_1'
FRONT_BUILD_CONTAINER_NAME = 'forcad_react_builder_1'


def wait_for_container(name):
    command = ['docker', 'wait', name]
    result = int(subprocess.check_output(command).decode().strip())
    if result != 0:
        print(f'Error in container {name}')
        p = subprocess.Popen(['docker-compose', 'logs'], cwd=PROJECT_DIR)
        p.wait()
        exit(1)


def wait_all():
    wait_for_container(INITIALIZER_CONTAINER_NAME)
    wait_for_container(FRONT_BUILD_CONTAINER_NAME)


if __name__ == '__main__':
    wait_all()
