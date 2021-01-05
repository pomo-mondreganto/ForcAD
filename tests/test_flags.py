import re
import socket
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from unittest import TestCase

import requests
from psycopg2 import pool, extras

PROJECT_DIR = Path(__file__).absolute().resolve().parents[1]
BACKEND_DIR = PROJECT_DIR / 'backend'
TESTS_DIR = PROJECT_DIR / 'tests'
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(TESTS_DIR))

import config
from helpers import wait_rounds


class FlagSubmitTestCase(TestCase):
    def setUp(self) -> None:
        command = ['./control.py', 'print_tokens']
        out = subprocess.check_output(command, cwd=PROJECT_DIR)
        out = out.decode().split('\n')
        for line in out:
            if not line:
                continue
            token = line.strip().split(':')[1]
            if 'working' in line:
                self.working_token = token
            elif 'inactive' not in line:
                self.unreachable_token = token

        database_config = config.get_db_config()
        database_config['host'] = '127.0.0.1'
        self.db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            **database_config,
        )

    def get_last_flags_from_db(self, team_token):
        conn = self.db_pool.getconn()
        curs = conn.cursor(cursor_factory=extras.RealDictCursor)

        query = '''
        SELECT * FROM flags F
        INNER JOIN teams T on F.team_id = T.id
        WHERE round >= (SELECT MAX(round) - 3 FROM FLAGS) AND T.token = %s
        '''
        curs.execute(query, (team_token,))
        return curs.fetchall()

    def submit_flags_to_tcp(self, token, flags=None, token_valid=True):
        sock = socket.socket()
        sock.connect(('127.0.0.1', 31337))
        time.sleep(0.5)
        greeting = sock.recv(1024).decode()
        self.assertIn('Welcome', greeting)
        self.assertIn('team token', greeting)
        sock.send((token + '\n').encode())
        time.sleep(0.5)
        response = sock.recv(1024).decode()
        if not token_valid:
            self.assertIn('Invalid', response)
            sock.close()
            return []

        self.assertIn('enter your flags', response)
        results = []
        for flag in flags:
            sock.send((flag + '\n').encode())
            time.sleep(0.5)
            response = sock.recv(1024).decode()
            results.append(response)

        sock.close()
        return results

    def submit_flags_to_http(self, token, flags=None, token_valid=True):
        response = requests.put(
            'http://127.0.0.1:8080/flags/',
            json=flags,
            headers={'X-Team-Token': token},
        )

        if not token_valid:
            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response.json())
            self.assertIn('Invalid', response.json()['error'])
            return []

        self.assertTrue(response.ok)

        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), len(flags))

        results = []
        for need, item in zip(flags, data):
            self.assertIn('msg', item)
            self.assertIn('flag', item)
            self.assertEqual(item['flag'], need)

            message = item['msg']

            self.assertIn(f'[{need}] ', message)

            match = re.fullmatch(
                f'\\[{need}] \\w+.*',
                message,
            )
            self.assertTrue(match is not None, msg=f'{message} is incorrect')

        return results

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

    def run_submission_tests(self, submit_func, flags):
        submit_func(
            token='invalid token',
            flags=[],
            token_valid=False,
        )

        results = submit_func(
            token=self.unreachable_token,
            flags=flags,
            token_valid=True,
        )

        for res in results:
            res = res.lower()
            self.assertIn('accepted', res)

        results = submit_func(
            token=self.unreachable_token,
            flags=flags,
            token_valid=True,
        )

        for res in results:
            res = res.lower()
            self.assertNotIn('accepted', res)
            self.assertIn('already stolen', res)

        results = submit_func(
            token=self.working_token,
            flags=flags,
            token_valid=True,
        )

        for res in results:
            res = res.lower()
            self.assertNotIn('accepted', res)
            self.assertIn('own', res)

        results = submit_func(
            token=self.unreachable_token,
            flags=['INVALID_FLAG', 'A' * 31 + '='],
            token_valid=True,
        )

        for res in results:
            res = res.lower()
            self.assertNotIn('accepted', res)
            self.assertIn('invalid', res)

    def test_flag_submission(self):
        ok_flags = self.get_last_flags_from_db(self.working_token)
        ok_flags = [flag['flag'] for flag in ok_flags]

        self.assertTrue(len(ok_flags) > 1)

        first_batch = ok_flags[:len(ok_flags) // 2]
        second_batch = ok_flags[len(ok_flags) // 2:]

        self.run_submission_tests(self.submit_flags_to_tcp, first_batch)
        self.run_submission_tests(self.submit_flags_to_http, second_batch)

        wait_rounds(1.5)

        teams = self.get_teams()
        all_stolen = 0
        all_lost = 0
        for team in teams:
            hist = self.get_team_history(team['id'])
            per_task = defaultdict(list)

            for each in hist:
                if 'working' not in team['name']:
                    self.assertEqual(int(each['lost']), 0)
                per_task[each['task_id']].append(each)

            per_task = list(map(
                lambda y: sorted(
                    y,
                    key=lambda x: (
                        lambda z: (
                            tuple(map(int, z.split('-'))),
                        )
                    )(x['timestamp']),
                )[-1],
                per_task.values(),
            ))

            all_stolen += sum(map(lambda x: int(x['stolen']), per_task))
            all_lost += sum(map(lambda x: int(x['lost']), per_task))

        self.assertEqual(all_stolen, len(ok_flags))
        self.assertEqual(all_lost, len(ok_flags))
