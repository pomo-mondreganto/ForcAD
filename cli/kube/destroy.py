import json

import click

from cli import utils, constants
from .utils import get_terraform_outputs


@click.command(help='Destroy Yandex.Cloud Kubernetes cluster')
@click.confirmation_option(
    prompt='Are you sure? This will permanently destroy '
           'all resources created for ForcAD.'
)
def destroy():
    tf_out = get_terraform_outputs()
    cluster_id = tf_out['cluster-id']['value']
    registry_id = tf_out['registry-id']['value']
    entry_name = f'yc-managed-k8s-{cluster_id}'

    to_unset = [
        f'users.{entry_name}',
        'contexts.yc-forcad',
        f'clusters.{entry_name}'
    ]
    for entry in to_unset:
        utils.run_command(['kubectl', 'config', 'unset', entry])

    click.echo('Cleaning up the registry', err=True)
    cmd = [
        'yc', 'container', 'image', 'list',
        '--registry-id', registry_id,
        '--format', 'json',
    ]
    registry_images = json.loads(utils.get_output(cmd))
    for image in registry_images:
        image_id = image['id']
        image_name = image['name']
        click.echo(f'Removing image {image_name}', err=True)
        utils.run_command(['yc', 'container', 'image', 'delete', image_id])

    utils.run_command(
        ['terraform', 'destroy', '-auto-approve'],
        cwd=constants.TERRAFORM_DIR,
    )

    utils.run_command(['skaffold', 'config', 'unset', 'default-repo'])
