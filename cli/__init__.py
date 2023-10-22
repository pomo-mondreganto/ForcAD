import click

from . import base


@click.group()
def cli():
    pass


base.register(cli)

__all__ = ('cli',)
