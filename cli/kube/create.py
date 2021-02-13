import click

from cli import utils, constants
from .utils import get_terraform_outputs


@click.command(help='Create Yandex.Cloud Kubernetes cluster for ForcAD')
def create():
    utils.run_command(['terraform', 'init'], cwd=constants.TERRAFORM_DIR)

    credentials_path = constants.TERRAFORM_DIR / 'credentials.auto.tfvars'
    if not credentials_path.exists():
        zone_choices = click.Choice([f'ru-central1-{c}' for c in 'abc'])

        data = {
            "yandex_cloud_token": click.prompt('Enter your YC OAuth token'),
            "cloud_id": click.prompt('Enter your YC cloud id'),
            "folder_id": click.prompt('Enter your YC folder id'),
            "zone": click.prompt(
                'In which zone will you deploy ForcAD?',
                type=zone_choices,
            ),
        }

        credentials_path.write_text(utils.dump_tf_config(data))

    utils.run_command(['terraform', 'plan'], cwd=constants.TERRAFORM_DIR)
    click.confirm('Does the plan above look ok?', abort=True)

    click.echo('Applying the plan with Terraform')
    utils.run_command(
        ['terraform', 'apply', '-auto-approve'],
        cwd=constants.TERRAFORM_DIR,
    )

    tf_out = get_terraform_outputs()
    cluster_id = tf_out['cluster-id']['value']
    folder_id = tf_out['folder-id']['value']
    registry_id = tf_out['registry-id']['value']

    click.echo('Adding cluster config to kubectl')
    cmd = [
        'yc', 'managed-kubernetes',
        'cluster', 'get-credentials',
        '--id', cluster_id,
        '--folder-id', folder_id,
        '--context-name', 'yc-forcad',
        '--external', '--force',
    ]
    utils.run_command(cmd)

    click.echo('New kubectl config:')
    utils.run_command(['kubectl', 'config', 'view'])

    click.echo('Configuring local docker to authenticate in YC registry')
    utils.run_command(['yc', 'container', 'registry', 'configure-docker'])

    repo = f'cr.yandex/{registry_id}'
    click.echo(f'Configuring skaffold to use repo {repo} by default')
    utils.run_command(['skaffold', 'config', 'set', 'default-repo', repo])
