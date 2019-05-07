from celery import Celery

import config

celery_config = config.get_celery_config()

app = Celery(
    __name__,
    include=[
        'celery_tasks.tasks',
    ],
)

game_config = config.get_game_config()

app.conf.beat_schedule = {
    'process_round': {
        'task': 'celery_tasks.tasks.process_round',
        'schedule': game_config['round_time'],
    },
}

app.conf.update(celery_config)
