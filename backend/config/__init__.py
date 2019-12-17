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
    return AppConfig.get_main_config()['celery']
