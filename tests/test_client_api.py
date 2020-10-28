from unittest import TestCase

import requests


class ClientApiTestCase(TestCase):
    @property
    def url(self):
        return 'http://127.0.0.1:8080'

    def get_team_list(self):
        r = requests.get(f'{self.url}/api/client/teams/')
        self.assertTrue(r.ok)

        data = r.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        return data

    def get_task_list(self):
        r = requests.get(f'{self.url}/api/client/tasks/')
        self.assertTrue(r.ok)

        data = r.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        return data

    def test_status_page(self):
        r = requests.get(f'{self.url}/api/client/status/')
        self.assertTrue(r.ok)

    def test_attack_data_api(self):
        r = requests.get(f'{self.url}/api/client/attack_data/')
        self.assertTrue(r.ok)

        data = r.json()
        self.assertIsInstance(data, dict)

        teams = self.get_team_list()
        tasks = self.get_task_list()

        for task in tasks:
            if 'pfr' in task['name']:
                self.assertIn(task['name'], data)

                task_data = data[task['name']]
                self.assertIsInstance(task_data, dict)

                for team in teams:
                    if 'working' in team['name']:
                        self.assertIn(team['ip'], task_data)
                        team_data = task_data[team['ip']]

                        self.assertIsInstance(team_data, list)
                        self.assertGreater(len(team_data), 0)

    def test_teams_api(self):
        data = self.get_team_list()

        for team in data:
            self.assertIn('id', team)
            self.assertIn('name', team)
            self.assertIn('ip', team)
            self.assertIn('highlighted', team)
            self.assertNotIn('token', team)

            if 'highlighted' in team['name']:
                self.assertTrue(team['highlighted'])
            else:
                self.assertFalse(team['highlighted'])

    def test_tasks_api(self):
        data = self.get_task_list()

        for task in data:
            self.assertIn('id', task)
            self.assertIn('name', task)

    def test_team_history(self):
        r = requests.get(f'{self.url}/api/client/teams/1/')
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

            self.assertNotIn('public_message', teamtask)
            self.assertNotIn('private_message', teamtask)
            self.assertNotIn('command', teamtask)
