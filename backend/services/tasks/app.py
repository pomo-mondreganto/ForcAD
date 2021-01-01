from celery import Celery

import config
from lib import storage
from round_processor import get_round_processor

celery_config = config.get_celery_config()

app = Celery(
    __name__,
    include=[
        'auxiliary',
        'actions',
        'handlers',
        'modes',
    ],
)

app.conf.update(celery_config)

game_config = storage.game.get_current_global_config()

if game_config.game_mode == 'blitz':
    tasks = storage.tasks.get_tasks()

    beat_schedule = {}
    puts_processor = get_round_processor(
        round_type='puts',
    )
    app.register_task(puts_processor)
    beat_schedule['process_puts_round'] = {
        'task': puts_processor.name,
        'schedule': game_config.round_time,
    }

    for task in tasks:
        check_get_processor = get_round_processor(
            round_type='check_gets',
            task_id=task.id,
        )
        app.register_task(check_get_processor)
        beat_schedule[f'process_check_gets_{task.id}_round'] = {
            'task': check_get_processor.name,
            'schedule': task.get_period,
        }
else:
    app.register_task(
        get_round_processor(round_type='full')
    )
    beat_schedule = {
        'process_full_round': {
            'task': 'tasks.round_processor.RoundProcessor_full',
            'schedule': game_config.round_time,
        },
    }

app.conf.beat_schedule = beat_schedule
