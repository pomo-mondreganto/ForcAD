import json

import click

from cli import utils, constants
from cli.kube.setup import setup
from cli.kube.validate import validate
from .utils import get_terraform_outputs


@click.command(help='Create Yandex.Cloud Kubernetes cluster for ForcAD')
@click.pass_context
def create(ctx: click.Context):
    ctx.invoke(validate, full=False, yandex=True)
    utils.backup_config()
    basic_config = utils.load_basic_config()
    config = utils.setup_auxiliary_structure(basic_config)

    utils.dump_config(config)

    utils.run_command(['terraform', 'init'], cwd=constants.TERRAFORM_DIR)

    if not constants.TF_CREDENTIALS_PATH.exists():
        zone_choices = click.Choice([f'ru-central1-{c}' for c in 'abc'])

        data = {
            "yandex_cloud_token": click.prompt('Enter your YC OAuth token'),
            "yandex_cloud_id": click.prompt('Enter your YC cloud id'),
            "yandex_folder_id": click.prompt('Enter your YC folder id'),
            "yandex_zone": click.prompt(
                'In which zone will you deploy ForcAD?',
                type=zone_choices,
                default=zone_choices.choices[0],
            ),
        }
    else:
        data = json.loads(constants.TF_CREDENTIALS_PATH.read_text())

    data['db_password'] = config.storages.db.password
    data['db_user'] = config.storages.db.user
    data['db_name'] = config.storages.db.dbname

    constants.TF_CREDENTIALS_PATH.write_text(json.dumps(data))

    utils.run_command(['terraform', 'plan'], cwd=constants.TERRAFORM_DIR)
    click.confirm(
        click.style('Does the plan above look ok?', bold=True),
        abort=True,
    )

    utils.print_bold('Applying the plan with Terraform')
    utils.run_command(
        ['terraform', 'apply', '-auto-approve'],
        cwd=constants.TERRAFORM_DIR,
    )

    tf_out = get_terraform_outputs()
    cluster_id = tf_out['cluster-id']['value']
    folder_id = tf_out['folder-id']['value']
    registry_id = tf_out['registry-id']['value']
    postgres_fqdn = tf_out['postgres-fqdn']['value']
    redis_fqdn = tf_out['redis-fqdn']['value']

    utils.print_bold('Adding cluster config to kubectl')
    cmd = [
        'yc', 'managed-kubernetes',
        'cluster', 'get-credentials',
        '--id', cluster_id,
        '--folder-id', folder_id,
        '--context-name', 'yc-forcad',
        '--external', '--force',
    ]
    utils.run_command(cmd)

    utils.print_bold('New kubectl config:')
    utils.run_command(['kubectl', 'config', 'view'])

    utils.print_bold('Configuring local docker to authenticate in YC registry')
    utils.run_command(['yc', 'container', 'registry', 'configure-docker'])

    repo = f'cr.yandex/{registry_id}'
    utils.print_bold(f'Configuring skaffold to use repo {repo} by default')
    utils.run_command(['skaffold', 'config', 'set', 'default-repo', repo])

    database = f'{postgres_fqdn}:6432'
    redis = f'{redis_fqdn}:6379'

    utils.print_bold(f'Postgres full address is {database}')
    utils.print_bold(f'Redis full address is {redis}')

    ctx.invoke(setup, database=database, redis=redis, rabbitmq=None)
