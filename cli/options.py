import click


def with_fast_option(func):
    click.option(
        '--fast',
        is_flag=True,
        help='Use faster build with prebuilt images',
    )(func)


def with_workers_option(func):
    return click.option(
        '-w', '--workers',
        type=int,
        metavar='N',
        default=1,
        help='Number of celery worker instances',
    )(func)
