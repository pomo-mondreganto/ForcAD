import os

import shutil

# backend
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_BASE = os.path.dirname(TESTS_DIR)

dst = os.path.join(PROJECT_BASE, 'checkers/test_service')
if os.path.exists(dst):
    shutil.rmtree(dst)

shutil.copytree(
    os.path.join(TESTS_DIR, 'service/checker'),
    os.path.join(PROJECT_BASE, 'checkers/test_service'),
)

dst = os.path.join(PROJECT_BASE, 'checkers/requirements.txt')
if os.path.exists(dst):
    os.remove(dst)

shutil.copy(
    os.path.join(TESTS_DIR, 'service/checker/requirements.txt'),
    os.path.join(PROJECT_BASE, 'checkers/requirements.txt'),
)

dst = os.path.join(PROJECT_BASE, 'backend/config/test_config.yml')
if os.path.exists(dst):
    os.remove(dst)

shutil.copy(
    os.path.join(TESTS_DIR, 'service/test_data/config.yml'),
    os.path.join(PROJECT_BASE, 'backend/config/test_config.yml'),
)
