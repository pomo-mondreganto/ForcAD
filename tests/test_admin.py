import os
import sys
from unittest import TestCase

import requests

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_DIR, 'backend')
TESTS_DIR = os.path.join(PROJECT_DIR, 'tests')
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, TESTS_DIR)


class TeamsTestCase(TestCase):
    def get_teams(self):
        r = requests.get(f'http://127.0.0.1:8080/api/admin/teams/')
        self.assertTrue(r.ok)

        data = r.json()
        return data

    def test_teams_api(self):
        was_teams = self.get_teams()

        new_team_data = {'name': 'Test created', 'highlighted': False, 'ip': '127.0.0.1'}
        r = requests.post('http://127.0.0.1/api/admin/teams/', json=new_team_data)
        self.assertEqual(r.status_code, 201)

        full_data = r.json()
        self.assertTrue(full_data.get('active'))

        for key in new_team_data.keys():
            self.assertEqual(new_team_data[key], full_data.get(key))

        new_teams = self.get_teams()
        self.assertIn(full_data, new_teams)
        self.assertEqual(len(was_teams) + 1, len(new_teams))

        update_data = {'name': 'Test updated', 'highlighted': True, 'active': True, 'ip': '127.0.0.3',
                       'token': full_data['token']}
        r = requests.put(f'http://127.0.0.1/api/admin/teams/{full_data["id"]}/', json=update_data)
        self.assertTrue(r.ok)

        full_data = r.json()

        for key in update_data.keys():
            self.assertEqual(update_data[key], full_data.get(key))

        new_teams = self.get_teams()
        self.assertIn(full_data, new_teams)
        self.assertEqual(len(was_teams) + 1, len(new_teams))

        r = requests.delete(f'http://127.0.0.1/api/admin/teams/{full_data["id"]}/')
        self.assertTrue(r.ok)

        new_teams = self.get_teams()
        full_data['active'] = False
        self.assertIn(full_data, new_teams)
        self.assertEqual(len(was_teams) + 1, len(new_teams))


class TasksTestCase(TestCase):
    def get_tasks(self):
        r = requests.get(f'http://127.0.0.1:8080/api/admin/tasks/')
        self.assertTrue(r.ok)

        data = r.json()
        return data

    def test_teams_api(self):
        was_tasks = self.get_tasks()

        new_task_data = {
            'name': 'test_created',
            'checker': '/checkers/test_service/gevent_checker.py',
            'gets': 2,
            'puts': 2,
            'places': 5,
            'checker_timeout': 10,
            'env_path': '/checkers/bin/',
            'checker_type': 'forcad_gevent_pfr',
            'get_period': 20,
            'default_score': 2500,
        }
        r = requests.post('http://127.0.0.1/api/admin/tasks/', json=new_task_data)
        self.assertEqual(r.status_code, 201)

        full_data = r.json()

        for key in new_task_data.keys():
            self.assertEqual(new_task_data[key], full_data.get(key))

        new_tasks = self.get_tasks()
        self.assertIn(full_data, new_tasks)
        self.assertEqual(len(was_tasks) + 1, len(new_tasks))

        update_data = {
            'name': 'test_updated',
            'checker': '/checkers/test_service/gevent_checker.py',
            'gets': 1,
            'puts': 1,
            'places': 3,
            'checker_timeout': 15,
            'env_path': '/checkers/bin/',
            'checker_type': 'forcad_gevent',
            'get_period': 30,
            'default_score': 2000,
            'active': True,
        }

        r = requests.put(f'http://127.0.0.1/api/admin/tasks/{full_data["id"]}/', json=update_data)
        self.assertTrue(r.ok)

        full_data = r.json()

        self.assertTrue(full_data.get('active'))

        for key in update_data.keys():
            self.assertEqual(update_data[key], full_data.get(key))

        new_tasks = self.get_tasks()
        self.assertIn(full_data, new_tasks)
        self.assertEqual(len(was_tasks) + 1, len(new_tasks))

        r = requests.delete(f'http://127.0.0.1/api/admin/tasks/{full_data["id"]}/')
        self.assertTrue(r.ok)

        new_tasks = self.get_tasks()
        full_data['active'] = False
        self.assertIn(full_data, new_tasks)
        self.assertEqual(len(was_tasks) + 1, len(new_tasks))
