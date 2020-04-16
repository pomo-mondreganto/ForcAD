import os
import sys
from unittest import TestCase

import requests

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_DIR, 'backend')
TESTS_DIR = os.path.join(PROJECT_DIR, 'tests')
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, TESTS_DIR)

from helpers import wait_rounds


class GameStatusTestCase(TestCase):
    def setUp(self) -> None:
        wait_rounds(3)

    def get_teams(self):
        r = requests.get(f'http://127.0.0.1:8080/api/teams/')
        self.assertTrue(r.ok)

        data = r.json()
        return data

    def get_team_history(self, team_id):
        r = requests.get(f'http://127.0.0.1:8080/api/teams/{team_id}/')
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
