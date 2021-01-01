import secrets

from flask import request, jsonify

import config
from lib import storage
from .utils import abort_with_error


def check_session():
    if 'session' not in request.cookies:
        abort_with_error('No session set', 403)

    session = request.cookies['session']
    with storage.utils.get_redis_storage().pipeline(transaction=False) as pipe:
        data, = pipe.get(f'session:{session}').execute()

    creds = config.get_web_credentials()

    if data != creds['username']:
        abort_with_error('Invalid session', 403)

    return True


def set_session(session, username):
    with storage.utils.get_redis_storage().pipeline(transaction=False) as pipe:
        pipe.set(f'session:{session}', username).execute()


def login():
    username = request.json.get('username')
    password = request.json.get('password')

    creds = config.get_web_credentials()
    if username != creds['username'] or password != creds['password']:
        abort_with_error('Invalid credentials', 403)

    session = secrets.token_hex(32)
    set_session(session, username)

    response = jsonify({'status': 'ok'})
    response.set_cookie('session', session, httponly=True)
    return response


def status():
    check_session()
    return jsonify({'status': 'ok'})
