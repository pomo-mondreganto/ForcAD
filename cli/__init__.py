import click

from . import base, kube


@click.group()
def cli():
    pass


base.register(cli)

cli.add_command(kube.cli)

__all__ = ('cli',)
