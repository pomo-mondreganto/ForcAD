import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sanic.response import json as json_response

import storage
from helplib import models

from .base import make_err_response


class TeamApi:
    def __init__(self, bp):
        bp.add_route(self.list, '/teams/', methods=['GET'])
        bp.add_route(self.create, '/teams/', methods=['POST'])
        bp.add_route(self.update, '/teams/<team_id:int>/', methods=['PUT'])
        bp.add_route(self.delete, '/teams/<team_id:int>/', methods=['DELETE'])

    @staticmethod
    async def list(_request):
        teams = await storage.teams.get_all_teams_async()
        dumped = [team.to_dict() for team in teams]
        return json_response(dumped)

    @staticmethod
    async def create(request):
        try:
            data = request.json
            data['token'] = models.Team.generate_token()
            team = models.Team.from_dict(data)
        except TypeError as e:
            return make_err_response(f'Invalid team data: {e}')

        created = await storage.teams.create_team(team)
        return json_response(created.to_dict(), status=201)

    @staticmethod
    async def update(request, team_id):
        try:
            data = request.json
            data['id'] = team_id
            team = models.Team.from_dict(request.json)
        except TypeError as e:
            return make_err_response(f'Invalid team data: {e}')

        updated = await storage.teams.update_team(team)
        return json_response(updated.to_dict())

    @staticmethod
    async def delete(_request, team_id):
        await storage.teams.delete_team(team_id)
        return json_response('ok')
