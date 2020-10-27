from sanic.response import json as json_response

from lib import models, storage, helpers
from .api_base import ApiSet
from .base import make_err_response


class TeamApi(ApiSet):
    model = 'team'

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
        await helpers.events.init_scoreboard_async()
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
        await helpers.events.init_scoreboard_async()
        return json_response(updated.to_dict())

    @staticmethod
    async def destroy(_request, team_id):
        await storage.teams.delete_team(team_id)
        await helpers.events.init_scoreboard_async()
        return json_response('ok')
