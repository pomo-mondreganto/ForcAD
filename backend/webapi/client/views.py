import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import asyncio

from sanic import Blueprint
from sanic.response import json as json_response, html, text

import storage
from helplib import models

client_bp = Blueprint('client_api')


@client_bp.route('/teams/')
async def get_teams(_request):
    redis_aio = await storage.get_async_redis_storage()
    pipe = redis_aio.pipeline()

    await storage.teams.teams_async_getter(redis_aio, pipe)
    teams, = await pipe.execute()
    teams = [
        models.Team.from_json(team).to_dict_for_participants()
        for team in teams
    ]

    return json_response(teams)


@client_bp.route('/tasks/')
async def get_tasks(_request):
    redis_aio = await storage.get_async_redis_storage()
    pipe = redis_aio.pipeline()

    await storage.tasks.tasks_async_getter(redis_aio, pipe)
    tasks, = await pipe.execute()
    tasks = [
        models.Task.from_json(task).to_dict_for_participants()
        for task in tasks
    ]

    return json_response(tasks)


@client_bp.route('/config/')
async def get_game_config(_request):
    redis_aio = await storage.get_async_redis_storage()
    pipe = redis_aio.pipeline()

    await storage.game.global_config_async_getter(redis_aio, pipe)
    conf, = await pipe.execute()
    conf = models.GlobalConfig.from_json(conf).to_dict()

    return json_response(conf)


@client_bp.route('/attack_data/')
async def serve_attack_data(_request):
    attack_data = await storage.game.get_attack_data(asyncio.get_event_loop())
    return text(attack_data, content_type='application/json')


# noinspection PyUnresolvedReferences
@client_bp.route('/teams/<team_id:int>/')
async def get_team_history(_request, team_id):
    teamtasks = await storage.tasks.get_teamtasks_of_team_async(
        team_id=team_id,
    )
    teamtasks = storage.tasks.filter_teamtasks_for_participants(teamtasks)
    return json_response(teamtasks)


@client_bp.route('/status/')
async def status(_request):
    return html("OK")
