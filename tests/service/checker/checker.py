#!/usr/bin/env python3

import requests
import sys
from checklib import *

PORT = 10000


def put(host, _flag_id, flag, vuln):
    new_id = rnd_string(10)
    r = requests.post(
        f'http://{host}:{PORT}/put/',
        json={
            'id': new_id,
            'vuln': vuln,
            'flag': flag,
        },
        timeout=2,
    )
    check_response(r, 'Could not put flag')
    cquit(Status.OK, new_id)


def get(host, flag_id, flag, vuln):
    r = requests.get(
        f'http://{host}:{PORT}/get/',
        params={
            'id': flag_id,
            'vuln': vuln,
        },
        timeout=2,
    )
    check_response(r, 'Could not get flag')
    data = get_json(r, 'Could not get flag')
    assert_in('flag', data, 'Could not get flag')
    assert_eq(data['flag'], flag, 'Could not get flag')
    cquit(Status.OK)


def check(host):
    r = requests.get(f'http://{host}:{PORT}/ping/', timeout=2)
    check_response(r, 'Check failed')
    cquit(Status.OK)


if __name__ == '__main__':
    action, *args = sys.argv[1:]
    try:
        if action == "check":
            host, = args
            check(host)
        elif action == "put":
            host, flag_id, flag, vuln = args
            put(host, flag_id, flag, vuln)
        elif action == "get":
            host, flag_id, flag, vuln = args
            get(host, flag_id, flag, vuln)
        else:
            cquit(Status.ERROR, 'System error', 'Unknown action: ' + action)

        cquit(Status.ERROR)
    except (
    requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
        cquit(Status.DOWN, 'Connection error')
    except SystemError:
        raise
    except Exception as e:
        cquit(Status.ERROR, 'System error', str(e))
