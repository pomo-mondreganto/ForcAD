import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import asyncio
from kombu.utils import json

from sanic import Sanic
from sanic.response import json as json_response, html
from sanic_cors import CORS

import storage
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
    game_state = await storage.game.get_game_state_async(loop)

    teams = await storage.teams.get_teams_async(loop)
    teams = [team.to_dict_for_participants() for team in teams]
    tasks = await storage.tasks.get_tasks_async(loop)
    tasks = [task.to_dict_for_participants() for task in tasks]
    if not game_state:
        state = ''
    else:
        state = game_state.to_dict()

    game_config = storage.game.get_current_global_config()
    game_config = game_config.to_dict()

    data_to_send = {
        'state': state,
        'teams': teams,
        'tasks': tasks,
        'config': game_config,
    }

    await sio.emit(
        'init_scoreboard',
        {'data': json.dumps(data_to_send)},
        namespace='/game_events',
        room=sid,
    )


@app.route('/api/teams/')
async def get_teams(_request):
    teams = await storage.teams.get_teams_async(asyncio.get_event_loop())
    teams = [team.to_dict_for_participants() for team in teams]
    return json_response(teams)


@app.route('/api/tasks/')
async def get_tasks(_request):
    tasks = await storage.tasks.get_tasks_async(asyncio.get_event_loop())
    tasks = [task.to_dict_for_participants() for task in tasks]
    return json_response(tasks)


@app.route('/api/config/')
async def get_game_config(_request):
    game_config = storage.game.get_current_global_config()
    return json_response(game_config.to_dict())


# noinspection PyUnresolvedReferences
@app.route('/api/teams/<team_id:int>/')
async def get_team_history(_request, team_id):
    teamtasks = storage.tasks.get_teamtasks_of_team_for_participants(team_id=team_id)
    return json_response(teamtasks)


@app.route('/api/status/')
async def status(_request):
    return html("OK")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
