import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

import asyncio

from sanic import Sanic
from sanic.response import html
import storage
from aioredis.pubsub import Receiver

import socketio

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)


@app.listener('before_server_start')
async def before_server_start(_sanic, loop):
    mpsc = Receiver(loop=loop)
    redis = await storage.get_async_redis_pool(loop)
    await redis.subscribe(mpsc.channel('scoreboard'))
    sio.start_background_task(background_task, mpsc)


async def background_task(mpsc):
    async for channel, msg in mpsc.iter():
        try:
            message = msg.decode()
        except AttributeError:
            pass
        else:
            await sio.emit('update_scoreboard', {'data': message}, namespace='/test')


@sio.on('connect', namespace='/test')
async def test_connect(_sid, _environ):
    game_state = await storage.game.get_game_state_async(asyncio.get_event_loop())

    teams = storage.teams.get_teams()
    teams = [team.to_json() for team in teams]
    tasks = storage.tasks.get_tasks()
    tasks = [task.to_json_for_participants() for task in tasks]
    if not game_state:
        state = ''
    else:
        state = game_state.to_json()

    await sio.emit(
        'init_scoreboard',
        {
            'data': {
                'state': state,
                'teams': teams,
                'tasks': tasks,
            }
        },
        namespace='/test'
    )


@app.route('/')
async def index(_request):
    with open('templates/app.html') as f:
        return html(f.read())


if __name__ == '__main__':
    app.run(port=5002)
