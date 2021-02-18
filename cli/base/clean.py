import click

from cli import constants, utils


@click.command(help='Clean up after running')
def clean():
    environment = [
        constants.ADMIN_ENV_PATH,
        constants.POSTGRES_ENV_PATH,
        constants.RABBITMQ_ENV_PATH,
        constants.REDIS_ENV_PATH,
    ]
    for file in environment:
        utils.remove_file(file)

    base_compose_path = constants.BASE_DIR / constants.BASE_COMPOSE_FILE
    utils.remove_file(base_compose_path)

    utils.remove_dir(constants.DOCKER_VOLUMES_DIR)

    utils.print_success('Cleanup successful!')
