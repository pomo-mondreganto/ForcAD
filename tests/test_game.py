from unittest import TestCase

import requests
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).absolute().resolve().parents[1]
BACKEND_DIR = PROJECT_DIR / 'backend'
TESTS_DIR = PROJECT_DIR / 'tests'
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(TESTS_DIR))

from helpers import wait_rounds


class GameStatusTestCase(TestCase):
    def setUp(self) -> None:
        wait_rounds(3)

    def get_teams(self):
        r = requests.get('http://127.0.0.1:8080/api/client/teams/')
        self.assertTrue(r.ok)

        data = r.json()
        return data

    def get_team_history(self, team_id):
        r = requests.get(f'http://127.0.0.1:8080/api/client/teams/{team_id}/')
        self.assertTrue(r.ok)

        data = r.json()
        return data

    def test_team_statuses(self):
        teams = self.get_teams()

        for team in teams:
            if 'working' in team['name']:
                hist = self.get_team_history(team['id'])
                for each in hist:
                    self.assertIn(each['status'], ['-1', '101'])
            else:
                hist = self.get_team_history(team['id'])
                for each in hist:
                    self.assertNotEqual(each['status'], '101')
