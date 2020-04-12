import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import asyncio

from sanic import Sanic
from sanic.response import json as json_response, html, text
from sanic_cors import CORS

import storage
from helplib import models
import socketio

sio_manager = storage.get_async_sio_manager()
sio = socketio.AsyncServer(
    async_mode='sanic',
    client_manager=sio_manager,
    cors_allowed_origins=[],
)

app = Sanic('forcad_api')
app.enable_websocket(True)
CORS(app, supports_credentials=True, automatic_options=True)

sio.attach(app)


@sio.on('connect', namespace='/game_events')
async def handle_connect(sid, _environ):
    loop = asyncio.get_event_loop()
    redis_aio = await storage.get_async_redis_storage(loop)
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

    teams = [models.Team.from_json(team).to_dict_for_participants() for team in teams]
    tasks = [models.Task.from_json(task).to_dict_for_participants() for task in tasks]
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


@app.route('/api/teams/')
async def get_teams(_request):
    loop = asyncio.get_event_loop()
    redis_aio = await storage.get_async_redis_storage(loop)
    pipe = redis_aio.pipeline()

    await storage.teams.teams_async_getter(redis_aio, pipe)
    teams, = await pipe.execute()
    teams = [models.Team.from_json(team).to_dict_for_participants() for team in teams]

    return json_response(teams)


@app.route('/api/tasks/')
async def get_tasks(_request):
    loop = asyncio.get_event_loop()
    redis_aio = await storage.get_async_redis_storage(loop)
    pipe = redis_aio.pipeline()

    await storage.tasks.tasks_async_getter(redis_aio, pipe)
    tasks, = await pipe.execute()
    tasks = [models.Task.from_json(task).to_dict_for_participants() for task in tasks]

    return json_response(tasks)


@app.route('/api/config/')
async def get_game_config(_request):
    loop = asyncio.get_event_loop()
    redis_aio = await storage.get_async_redis_storage(loop)
    pipe = redis_aio.pipeline()

    await storage.game.global_config_async_getter(redis_aio, pipe)
    conf, = await pipe.execute()
    conf = models.GlobalConfig.from_json(conf).to_dict()

    return json_response(conf)


@app.route('/api/attack_data')
async def serve_attack_data(_request):
    attack_data = await storage.game.get_attack_data(asyncio.get_event_loop())
    return text(attack_data, content_type='application/json')


# noinspection PyUnresolvedReferences
@app.route('/api/teams/<team_id:int>/')
async def get_team_history(_request, team_id):
    loop = asyncio.get_event_loop()
    teamtasks = await storage.tasks.get_teamtasks_of_team_async(team_id=team_id, loop=loop)
    teamtasks = storage.tasks.filter_teamtasks_for_participants(teamtasks)
    return json_response(teamtasks)


@app.route('/api/status/')
async def status(_request):
    return html("OK")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
