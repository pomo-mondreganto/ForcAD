import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, 'config')

_storage_config = None


def get_storage_config() -> dict:
    global _storage_config

    if not _storage_config:
        conf_path = os.path.join(CONFIG_DIR, 'storage.yml')
        _storage_config = yaml.load(open(conf_path), Loader=yaml.FullLoader)

    return _storage_config


_game_config = None


def get_game_config() -> dict:
    global _game_config

    if not _game_config:
        conf_path = os.path.join(CONFIG_DIR, 'game.yml')
        _game_config = yaml.load(open(conf_path), Loader=yaml.FullLoader)

    return _game_config


_teams_config = None


def get_teams_config() -> dict:
    global _teams_config

    if not _teams_config:
        conf_path = os.path.join(CONFIG_DIR, 'teams.yml')
        _teams_config = yaml.load(open(conf_path), Loader=yaml.FullLoader)

    return _teams_config


_celery_config = None


def get_celery_config() -> dict:
    global _celery_config

    if not _celery_config:
        conf_path = os.path.join(CONFIG_DIR, 'celery.yml')
        _celery_config = yaml.load(open(conf_path), Loader=yaml.FullLoader)

    return _celery_config
