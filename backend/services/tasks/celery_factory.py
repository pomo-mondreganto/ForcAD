from celery import Celery

from lib import config


def get_celery_app():
    celery_config = config.get_celery_config()
    app = Celery(
        __name__,
        include=[
            'tasks.auxiliary',
            'tasks.actions',
            'tasks.handlers',
            'tasks.modes',
        ],
    )

    app.conf.update(celery_config)
    return app
