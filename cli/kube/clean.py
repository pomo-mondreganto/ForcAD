import click

from cli import constants, utils


@click.command(help='Clean up after running')
def clean():
    secrets = [
        constants.ADMIN_SECRET_PATH,
        constants.CONFIG_SECRET_PATH,
        constants.POSTGRES_SECRET_PATH,
        constants.RABBITMQ_SECRET_PATH,
        constants.REDIS_SECRET_PATH,
    ]
    for file in secrets:
        utils.remove_file(file)

    utils.remove_file(constants.KUSTOMIZATION_PATH)

    terraform_files = [
        constants.TF_CREDENTIALS_PATH,
        constants.TERRAFORM_DIR / 'terraform.tfstate',
        constants.TERRAFORM_DIR / 'terraform.tfstate.backup',
    ]
    for file in terraform_files:
        utils.remove_file(file)

    terraform_cache_path = constants.TERRAFORM_DIR / '.terraform'
    utils.remove_dir(terraform_cache_path)
