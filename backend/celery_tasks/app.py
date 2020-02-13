from celery import Celery

import celery_tasks.round_processor
import config
import storage

celery_config = config.get_celery_config()

app = Celery(
    __name__,
    include=[
        'celery_tasks.auxiliary',
        'celery_tasks.actions',
        'celery_tasks.handlers',
        'celery_tasks.modes',
    ],
)

app.conf.update(celery_config)

app.register_task(celery_tasks.round_processor.RoundProcessor())

game_config = storage.game.get_current_global_config()

app.conf.beat_schedule = {
    'process_round': {
        'task': 'celery_tasks.round_processor.RoundProcessor',
        'schedule': game_config.round_time,
    },
}
