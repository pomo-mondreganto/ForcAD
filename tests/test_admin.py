import os
import sys
from pathlib import Path
from unittest import TestCase

import requests

PROJECT_DIR = Path(__file__).absolute().resolve().parents[1]
BACKEND_DIR = PROJECT_DIR / 'backend'
TESTS_DIR = PROJECT_DIR / 'tests'
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(TESTS_DIR))


class AdminAuthMixin:
    def get_admin_sess(self):
        username = os.environ['ADMIN_USERNAME']
        password = os.environ['ADMIN_PASSWORD']

        s2 = requests.Session()
        r = s2.post(
            'http://127.0.0.1:8080/api/admin/login/',
            json={
                'username': username,
                'password': password,
            },
        )
        self.assertTrue(r.ok)

        return s2


class BaseAdminTestCase(TestCase, AdminAuthMixin):
    def test_unauthenticated(self):
        r = requests.get('http://127.0.0.1:8080/api/admin/teams/')
        self.assertFalse(r.ok)
        r = requests.get('http://127.0.0.1:8080/api/admin/tasks/')
        self.assertFalse(r.ok)

    def test_authentication(self):
        self.s1 = requests.Session()
        r = self.s1.post(
            'http://127.0.0.1:8080/api/admin/login/',
            json={
                'username': 'some_username',
                'password': 'invalid_password',
            },
        )
        self.assertFalse(r.ok)

        r = self.s1.get('http://127.0.0.1:8080/api/admin/teams/')
        self.assertFalse(r.ok)
        r = self.s1.get('http://127.0.0.1:8080/api/admin/tasks/')
        self.assertFalse(r.ok)

        self.s2 = self.get_admin_sess()
        r = self.s2.get('http://127.0.0.1:8080/api/admin/teams/')
        self.assertTrue(r.ok)
        r = self.s2.get('http://127.0.0.1:8080/api/admin/tasks/')
        self.assertTrue(r.ok)

    def tearDown(self):
        if hasattr(self, 's1'):
            self.s1.close()
        if hasattr(self, 's2'):
            self.s2.close()


class TeamsTestCase(TestCase, AdminAuthMixin):
    def setUp(self) -> None:
        self.s = self.get_admin_sess()

    def get_teams(self):
        r = self.s.get('http://127.0.0.1:8080/api/admin/teams/')
        self.assertTrue(r.ok)

        data = r.json()
        return data

    def test_teams_api(self):
        was_teams = self.get_teams()

        new_team_data = {
            'name': 'Test created',
            'highlighted': False,
            'ip': '127.0.0.1',
        }
        r = self.s.post(
            'http://127.0.0.1/api/admin/teams/',
            json=new_team_data,
        )
        self.assertEqual(r.status_code, 201)

        full_data = r.json()
        self.assertTrue(full_data.get('active'))

        for k, v in new_team_data.items():
            self.assertEqual(v, full_data.get(k))

        new_teams = self.get_teams()
        self.assertIn(full_data, new_teams)
        self.assertEqual(len(was_teams) + 1, len(new_teams))

        update_data = {
            'name': 'Test inactive',
            'highlighted': True,
            'active': True,
            'ip': '127.0.0.3',
            'token': full_data['token'],
        }
        r = self.s.put(
            f'http://127.0.0.1/api/admin/teams/{full_data["id"]}/',
            json=update_data,
        )
        self.assertTrue(r.ok)

        full_data = r.json()

        for k, v in update_data.items():
            self.assertEqual(v, full_data.get(k))

        new_teams = self.get_teams()
        self.assertIn(full_data, new_teams)
        self.assertEqual(len(was_teams) + 1, len(new_teams))

        r = self.s.delete(
            f'http://127.0.0.1/api/admin/teams/{full_data["id"]}/',
        )
        self.assertTrue(r.ok)

        new_teams = self.get_teams()
        full_data['active'] = False
        self.assertIn(full_data, new_teams)
        self.assertEqual(len(was_teams) + 1, len(new_teams))

    def tearDown(self):
        self.s.close()


class TasksTestCase(TestCase, AdminAuthMixin):
    def setUp(self) -> None:
        self.s = self.get_admin_sess()

    def get_tasks(self):
        r = self.s.get('http://127.0.0.1:8080/api/admin/tasks/')
        self.assertTrue(r.ok)

        data = r.json()
        return data

    def test_tasks_api(self):
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
        r = self.s.post(
            'http://127.0.0.1/api/admin/tasks/',
            json=new_task_data,
        )
        self.assertEqual(r.status_code, 201)

        full_data = r.json()

        for k, v in new_task_data.items():
            self.assertEqual(v, full_data.get(k))

        new_tasks = self.get_tasks()
        self.assertIn(full_data, new_tasks)
        self.assertEqual(len(was_tasks) + 1, len(new_tasks))

        update_data = {
            'name': 'test_updated_inactive',
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

        r = self.s.put(
            f'http://127.0.0.1/api/admin/tasks/{full_data["id"]}/',
            json=update_data,
        )
        self.assertTrue(r.ok)

        full_data = r.json()

        self.assertTrue(full_data.get('active'))

        for k, v in update_data.items():
            self.assertEqual(v, full_data.get(k))

        new_tasks = self.get_tasks()
        self.assertIn(full_data, new_tasks)
        self.assertEqual(len(was_tasks) + 1, len(new_tasks))

        r = self.s.delete(
            f'http://127.0.0.1/api/admin/tasks/{full_data["id"]}/',
        )
        self.assertTrue(r.ok)

        new_tasks = self.get_tasks()
        full_data['active'] = False
        self.assertIn(full_data, new_tasks)
        self.assertEqual(len(was_tasks) + 1, len(new_tasks))

    def tearDown(self):
        self.s.close()

    def test_teamtasks_api(self):
        r = self.s.get(
            'http://127.0.0.1:8080/api/admin/teamtasks/',
            params={'team_id': 1, 'task_id': 1},
        )
        self.assertTrue(r.ok)
