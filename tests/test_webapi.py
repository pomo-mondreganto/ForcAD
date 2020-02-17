from unittest import TestCase

import requests


class WebApiTestCase(TestCase):
    @property
    def url(self):
        return 'http://127.0.0.1:8080'

    def test_status_page(self):
        r = requests.get(f'{self.url}/api/status/')
        self.assertTrue(r.ok)

    def test_teams_api(self):
        r = requests.get(f'{self.url}/api/teams/')
        self.assertTrue(r.ok)

        data = r.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        for team in data:
            self.assertIn('id', team)
            self.assertIn('name', team)
            self.assertIn('ip', team)
            self.assertNotIn('token', team)

    def test_tasks_api(self):
        r = requests.get(f'{self.url}/api/tasks/')
        self.assertTrue(r.ok)

        data = r.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        for task in data:
            self.assertIn('id', task)
            self.assertIn('name', task)

    def test_team_history(self):
        r = requests.get(f'{self.url}/api/teams/1/')
        self.assertTrue(r.ok)

        data = r.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        for teamtask in data:
            self.assertIn('message', teamtask)
            self.assertIn('team_id', teamtask)
            self.assertEqual(teamtask['team_id'], '1')
            self.assertIn('task_id', teamtask)
            self.assertIn('stolen', teamtask)
            self.assertIn('lost', teamtask)
            self.assertIn('status', teamtask)
            self.assertIn('round', teamtask)

            self.assertNotIn('public_message', teamtask)
            self.assertNotIn('private_message', teamtask)
            self.assertNotIn('command', teamtask)
