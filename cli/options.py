import click


def with_fast_option(func):
    return click.option(
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


def with_external_services_option(func):
    wrapped = click.option(
        '--redis',
        metavar='ADDR',
        help='External redis address (disables built-in redis container)',
    )(func)
    wrapped = click.option(
        '--database',
        metavar='ADDR',
        help='External Postgres address (disables built-in postgres container)',
    )(wrapped)
    wrapped = click.option(
        '--rabbitmq',
        metavar='ADDR',
        help='External RabbitMQ address (disables built-in rabbitmq container)',
    )(wrapped)

    return wrapped
