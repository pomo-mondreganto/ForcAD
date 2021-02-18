from pathlib import Path

ADMIN_USER = 'forcad'

BASE_DIR = Path(__file__).absolute().resolve().parents[1]
BASE_COMPOSE_FILE = 'docker-compose-base.yml'
FAST_COMPOSE_FILE = 'docker-compose-fast.yml'
TESTS_COMPOSE_FILE = 'docker-compose-tests.yml'

DEPLOY_DIR = BASE_DIR / 'deploy'
SECRETS_DIR = DEPLOY_DIR / 'secrets'
KUSTOMIZATION_BASE_PATH = DEPLOY_DIR / 'kustomization.base.yml'
KUSTOMIZATION_PATH = DEPLOY_DIR / 'kustomization.yml'

TERRAFORM_DIR = DEPLOY_DIR / 'terraform'
TF_CREDENTIALS_PATH = TERRAFORM_DIR / 'credentials.auto.tfvars.json'

FULL_COMPOSE_PATH = BASE_DIR / 'docker-compose.yml'
CONFIG_PATH = BASE_DIR / 'config.yml'
VERSION_PATH = BASE_DIR / '.version'

DOCKER_CONFIG_DIR = BASE_DIR / 'docker_config'
DOCKER_VOLUMES_DIR = BASE_DIR / 'docker_volumes'

ADMIN_ENV_PATH = DOCKER_CONFIG_DIR / 'services/' / 'admin.env'
POSTGRES_ENV_PATH = DOCKER_CONFIG_DIR / 'postgres_environment.env'
RABBITMQ_ENV_PATH = DOCKER_CONFIG_DIR / 'rabbitmq_environment.env'
REDIS_ENV_PATH = DOCKER_CONFIG_DIR / 'redis_environment.env'

ADMIN_SECRET_PATH = SECRETS_DIR / 'admin.yml'
POSTGRES_SECRET_PATH = SECRETS_DIR / 'postgres.yml'
RABBITMQ_SECRET_PATH = SECRETS_DIR / 'rabbitmq.yml'
REDIS_SECRET_PATH = SECRETS_DIR / 'redis.yml'
CONFIG_SECRET_PATH = SECRETS_DIR / 'config.yml'

try:
    VERSION = VERSION_PATH.read_text().strip()
except FileNotFoundError:
    VERSION = 'latest'
