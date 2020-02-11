import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
CONFIG_FILENAME = 'config.yml'

if os.environ.get('TEST'):
    CONFIG_FILENAME = 'test_config.yml'
elif os.environ.get('LOCAL'):
    CONFIG_FILENAME = 'local_config.yml'


class AppConfig:
    _main_config = None

    @staticmethod
    def get_main_config():
        if not AppConfig._main_config:
            conf_path = os.path.join(CONFIG_DIR, CONFIG_FILENAME)
            with open(conf_path) as f:
                AppConfig._main_config = yaml.load(f, Loader=yaml.FullLoader)

        return AppConfig._main_config


def get_storage_config() -> dict:
    return AppConfig.get_main_config()['storages']


def get_global_config() -> dict:
    return AppConfig.get_main_config()['global']


def get_teams_config() -> list:
    return AppConfig.get_main_config()['teams']


def get_tasks_config() -> list:
    return AppConfig.get_main_config()['tasks']


def get_celery_config() -> dict:
    storages = get_storage_config()
    global_conf = get_global_config()

    redis_host = storages['redis'].get('host', 'redis')
    redis_port = storages['redis'].get('port', 6379)
    redis_pass = storages['redis'].get('password', None)
    redis_db = storages['redis'].get('db', 0)
    result_db = redis_db + 1

    amqp_host = storages['rabbitmq'].get('host', 'rabbitmq')
    amqp_user = storages['rabbitmq'].get('user', 'system_admin')
    amqp_port = storages['rabbitmq'].get('port', 5672)
    amqp_pass = storages['rabbitmq'].get('password', None)
    amqp_vhost = storages['rabbitmq'].get('vhost', 'forcad')
    broker_url = f'amqp://{amqp_user}:{amqp_pass}@{amqp_host}:{amqp_port}/{amqp_vhost}'

    if redis_pass is not None:
        result_backend = f'redis://:{redis_pass}@{redis_host}:{redis_port}/{result_db}'
    else:
        result_backend = f'redis://{redis_host}:{redis_port}/{result_db}'

    conf = {
        'accept_content': ['pickle'],
        'broker_url': broker_url,
        'result_backend': result_backend,
        'result_serializer': 'pickle',
        'task_serializer': 'pickle',
        'timezone': global_conf['timezone'],
        'worker_prefetch_multiplier': 1,
    }

    return conf
