from pathlib import Path

BASE_DIR = Path(__file__).absolute().resolve().parents[1]
BASE_COMPOSE_FILE = 'docker-compose-base.yml'
FAST_COMPOSE_FILE = 'docker-compose-fast.yml'
TESTS_COMPOSE_FILE = 'docker-compose-tests.yml'

FULL_COMPOSE_PATH = BASE_DIR / 'docker-compose.yml'
CONFIG_PATH = BASE_DIR / 'config.yml'
VERSION_PATH = BASE_DIR / '.version'

try:
    VERSION = VERSION_PATH.read_text().strip()
except FileNotFoundError:
    VERSION = 'latest'
