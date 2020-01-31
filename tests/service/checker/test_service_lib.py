import requests
from checklib import *

PORT = 10000


class CheckMachine:
    def __init__(self, host):
        self.host = host

    def ping(self):
        r = requests.get(f'http://{self.host}:{PORT}/ping/', timeout=2)
        check_response(r, 'Check failed')

    def put_flag(self, flag, vuln):
        new_id = rnd_string(10)
        r = requests.post(
            f'http://{self.host}:{PORT}/put/',
            json={
                'id': new_id,
                'vuln': vuln,
                'flag': flag,
            },
            timeout=2,
        )
        check_response(r, 'Could not put flag')

        return new_id

    def get_flag(self, flag_id, vuln):
        r = requests.get(
            f'http://{self.host}:{PORT}/get/',
            params={
                'id': flag_id,
                'vuln': vuln,
            },
            timeout=2,
        )
        check_response(r, 'Could not get flag')
        data = get_json(r, 'Invalid response from /get/')
        assert_in('flag', data, 'Could not get flag', status=Status.CORRUPT)
        return data['flag']
