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

game_config = storage.game.get_current_global_config()

if game_config.game_mode == 'blitz':
    tasks = storage.tasks.get_tasks()

    beat_schedule = {}
    puts_processor = celery_tasks.round_processor.get_round_processor(round_type='puts')
    app.register_task(puts_processor)
    beat_schedule['process_puts_round'] = {
        'task': puts_processor.name,
        'schedule': game_config.round_time,
    }

    for task in tasks:
        check_gets_processor = celery_tasks.round_processor.get_round_processor(
            round_type='check_gets',
            task_id=task.id,
        )
        app.register_task(check_gets_processor)
        beat_schedule[f'process_check_gets_{task.id}_round'] = {
            'task': check_gets_processor.name,
            'schedule': task.get_period,
        }
else:
    app.register_task(
        celery_tasks.round_processor.get_round_processor(round_type='full')
    )
    beat_schedule = {
        'process_full_round': {
            'task': 'celery_tasks.round_processor.RoundProcessor_full',
            'schedule': game_config.round_time,
        },
    }

app.conf.beat_schedule = beat_schedule
