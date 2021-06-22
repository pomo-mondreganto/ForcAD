from flask import request, jsonify

from lib import models, storage
from lib.helpers import events
from .api_base import ApiSet
from .utils import make_err_response


class TeamApi(ApiSet):
    model = 'team'

    @staticmethod
    def retrieve(team_id):
        teams = storage.teams.get_all_teams()
        try:
            team = next(filter(lambda x: x.id == team_id, teams))
        except StopIteration:
            return make_err_response('No such team', status=404)

        return jsonify(team.to_dict())

    @staticmethod
    def list():
        teams = storage.teams.get_all_teams()
        dumped = [team.to_dict() for team in teams]
        return jsonify(dumped)

    @staticmethod
    def create():
        try:
            data = request.json
            data['token'] = models.Team.generate_token()
            team = models.Team.from_dict(data)
        except TypeError as e:
            return make_err_response(f'Invalid team data: {e}')

        created = storage.teams.create_team(team)
        events.init_scoreboard()
        return jsonify(created.to_dict()), 201

    @staticmethod
    def update(team_id):
        try:
            data = request.json
            data['id'] = team_id
            team = models.Team.from_dict(request.json)
        except TypeError as e:
            return make_err_response(f'Invalid team data: {e}')

        updated = storage.teams.update_team(team)
        events.init_scoreboard()
        return jsonify(updated.to_dict())

    @staticmethod
    def destroy(team_id):
        storage.teams.delete_team(team_id)
        events.init_scoreboard()
        return jsonify('ok')
