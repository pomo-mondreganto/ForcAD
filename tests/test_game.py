import os
from unittest import TestCase

import requests
import sys

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_DIR, 'backend')
TESTS_DIR = os.path.join(PROJECT_DIR, 'tests')
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, TESTS_DIR)

from helpers import wait_rounds


class GameStatusTestCase(TestCase):
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
        wait_rounds(3)

        teams = self.get_teams()

        for team in teams:
            if 'working' in team['name']:
                hist = self.get_team_history(team['id'])
                for each in hist:
                    if each['round'] != '0':
                        self.assertEqual(each['status'], '101')
            else:
                hist = self.get_team_history(team['id'])
                for each in hist:
                    if each['round'] != '0':
                        self.assertNotEqual(each['status'], '101')
