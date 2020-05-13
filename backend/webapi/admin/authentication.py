import secrets

from functools import wraps
from sanic.exceptions import Forbidden
from sanic.response import json

import config
import storage


async def check_session(request):
    if 'session' not in request.cookies:
        raise Forbidden('No session set')

    session = request.cookies['session']
    redis_aio = await storage.get_async_redis_storage()
    data = await redis_aio.get(f'session:{session}')
    creds = config.get_web_credentials()

    if data != creds['username']:
        raise Forbidden('Invalid session')

    return True


async def set_session(session, username):
    redis_aio = await storage.get_async_redis_storage()
    await redis_aio.set(f'session:{session}', username)


async def login(request):
    username = request.json.get('username')
    password = request.json.get('password')

    creds = config.get_web_credentials()
    if username != creds['username'] or password != creds['password']:
        raise Forbidden('Invalid credentials')

    session = secrets.token_hex(32)
    await set_session(session, username)

    response = json({'status': 'ok'})
    response.cookies['session'] = session
    return response


async def status(request):
    await check_session(request)
    return json({'status': 'ok'})


def login_required(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        await check_session(request)
        return await func(request, *args, **kwargs)

    return wrapper
