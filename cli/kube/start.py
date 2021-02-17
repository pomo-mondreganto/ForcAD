import click

from cli import utils
from cli.constants import BASE_DIR
from .utils import get_resource_description


@click.command(help='Deploy to the the cluster using Skaffold')
@click.option(
    '--dev',
    is_flag=True,
    help='Use development configuration (with hot reload)',
)
def start(dev: bool, **_kwargs):
    utils.print_bold('Deploying using skaffold')
    cmd = [
        'skaffold',
        'dev' if dev else 'run',
        '-f', 'deploy/skaffold.yml'
    ]
    utils.run_command(cmd, cwd=BASE_DIR)
    utils.print_success('Deployed successfully!')

    utils.print_bold('Fetching the address for deployment')
    service_resource = get_resource_description(resource='service', name='nginx')
    ip = service_resource['status']['loadBalancer']['ingress'][0]['ip']
    utils.print_success(f'You can access ForcAD at http://{ip}')
