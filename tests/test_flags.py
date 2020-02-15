import os
from unittest import TestCase

import requests
import socket
import subprocess
import sys
import time
from psycopg2 import pool, extras

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)

import config


def wait_rounds(rounds):
    round_time = config.get_global_config()['round_time']
    time.sleep(rounds * round_time)


class FlagSubmitTestCase(TestCase):
    def setUp(self) -> None:
        command = ['./control.py', 'print_tokens']
        out = subprocess.check_output(command, cwd=PROJECT_DIR).decode().split('\n')
        for line in out:
            if not line:
                continue
            token = line.strip().split(':')[1]
            if 'working' in line:
                self.working_token = token
            else:
                self.unreachable_token = token

        database_config = config.get_storage_config()['db']
        database_config['host'] = '127.0.0.1'
        self.db_pool = pool.SimpleConnectionPool(minconn=1, maxconn=20, **database_config)

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

    def submit_flags_to_tcp_mux(self, token, flags=None, token_valid=True):
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
            return

        self.assertIn('enter your flags', response)
        results = []
        for flag in flags:
            sock.send((flag + '\n').encode())
            time.sleep(0.5)
            response = sock.recv(1024).decode()
            results.append(response)

        sock.close()
        return results

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

    def test_flag_submission(self):
        ok_flags = self.get_last_flags_from_db(self.working_token)
        ok_flags = [flag['flag'] for flag in ok_flags]

        self.submit_flags_to_tcp_mux(
            token='invalid token',
            flags=[],
            token_valid=False,
        )

        results = self.submit_flags_to_tcp_mux(
            token=self.unreachable_token,
            flags=ok_flags,
            token_valid=True,
        )

        for res in results:
            res = res.lower()
            self.assertIn('accepted', res)

        results = self.submit_flags_to_tcp_mux(
            token=self.unreachable_token,
            flags=ok_flags,
            token_valid=True,
        )

        for res in results:
            res = res.lower()
            self.assertNotIn('accepted', res)
            self.assertIn('already stolen', res)

        results = self.submit_flags_to_tcp_mux(
            token=self.working_token,
            flags=ok_flags,
            token_valid=True,
        )

        for res in results:
            res = res.lower()
            self.assertNotIn('accepted', res)
            self.assertIn('own', res)

        results = self.submit_flags_to_tcp_mux(
            token=self.working_token,
            flags=['INVALID_FLAG', 'A' * 31 + '='],
            token_valid=True,
        )

        for res in results:
            res = res.lower()
            self.assertNotIn('accepted', res)
            self.assertIn('invalid', res)

        wait_rounds(1.5)

        teams = self.get_teams()
        all_stolen = 0
        all_lost = 0
        for team in teams:
            hist = self.get_team_history(team['id'])
            last_round = max(map(lambda x: x['round'], hist))

            for each in hist:
                if 'working' not in team['name']:
                    self.assertEqual(each['lost'], 0)

                if each['round'] == last_round:
                    all_stolen += each['stolen']
                    all_lost += each['lost']

        self.assertEqual(all_stolen, len(ok_flags))
        self.assertEqual(all_lost, len(ok_flags))
