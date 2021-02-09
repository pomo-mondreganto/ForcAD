import click

from cli.utils import run_docker


@click.command(help='Scale any service (e.g. "celery 3" to set number of workers to 5)')
@click.option(
    '-s', '--service',
    type=(str, int),
    metavar='SERVICE INSTANCES',
    help='Service name & instance count. Can be specified multiple times.',
    multiple=True,
    required=True,
)
def scale(service):
    command = ['up', '-d', '--no-recreate']
    services = []
    for name, instances in service:
        command.append('--scale')
        command.append(f'{name}={instances}')
        services.append(name)
    command += services
    run_docker(command)
