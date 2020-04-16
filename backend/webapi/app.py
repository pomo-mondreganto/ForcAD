import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import asyncio

from sanic import Sanic, Blueprint
from sanic_cors import CORS

import storage
from helplib import models
import socketio
from webapi.monitoring import MonitorClient
from webapi import client, admin

sio_manager = storage.get_async_sio_manager()
sio = socketio.AsyncServer(
    async_mode='sanic',
    client_manager=sio_manager,
    cors_allowed_origins=[],
)

app = Sanic('forcad_api')
app.enable_websocket(True)
CORS(app, supports_credentials=True, automatic_options=True)

loop = asyncio.get_event_loop()
mon = MonitorClient(app)
mon.add_endpoint('/api/metrics')
loop.run_until_complete(mon.connect_consumer())

sio.attach(app)

bps = Blueprint.group(admin.admin_bp, client.client_bp, url_prefix='/api')
app.blueprint(bps)


@sio.on('connect', namespace='/game_events')
async def handle_connect(sid, _environ):
    redis_aio = await storage.get_async_redis_storage()
    pipe = redis_aio.pipeline()
    pipe.get('game_state')
    await storage.teams.teams_async_getter(redis_aio, pipe)
    await storage.tasks.tasks_async_getter(redis_aio, pipe)
    await storage.game.global_config_async_getter(redis_aio, pipe)
    state, teams, tasks, game_config = await pipe.execute()

    try:
        state = models.GameState.from_json(state).to_dict()
    except TypeError:
        state = None

    teams = [
        models.Team.from_json(team).to_dict_for_participants()
        for team in teams
    ]
    tasks = [
        models.Task.from_json(task).to_dict_for_participants()
        for task in tasks
    ]
    game_config = models.GlobalConfig.from_json(game_config).to_dict()

    data_to_send = {
        'state': state,
        'teams': teams,
        'tasks': tasks,
        'config': game_config,
    }

    await sio.emit(
        'init_scoreboard',
        {'data': data_to_send},
        namespace='/game_events',
        room=sid,
    )


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
