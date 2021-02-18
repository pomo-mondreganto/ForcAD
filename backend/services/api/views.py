from flask import Blueprint
from flask import jsonify, make_response

from lib import storage

client_bp = Blueprint('client_api', __name__)


@client_bp.route('/teams/')
def get_teams():
    teams = [team.to_dict_for_participants() for team in storage.teams.get_teams()]
    return jsonify(teams)


@client_bp.route('/tasks/')
def get_tasks():
    tasks = [task.to_dict_for_participants() for task in storage.tasks.get_tasks()]

    return jsonify(tasks)


@client_bp.route('/config/')
def get_game_config():
    cfg = storage.game.get_current_game_config().to_dict()
    return jsonify(cfg)


@client_bp.route('/attack_data/')
def serve_attack_data():
    attack_data = storage.attacks.get_attack_data()
    response = make_response(attack_data)
    response.headers['Content-Type'] = 'application/json'
    return response


@client_bp.route('/teams/<int:team_id>/')
def get_team_history(team_id):
    teamtasks = storage.tasks.get_teamtasks_for_team(team_id)
    teamtasks = storage.tasks.filter_teamtasks_for_participants(teamtasks)
    return jsonify(teamtasks)


@client_bp.route('/ctftime/')
def get_ctftime_scoreboard():
    standings = storage.game.construct_ctftime_scoreboard()
    if not standings:
        return jsonify({'error': 'not available'}), 400
    return jsonify(standings)


@client_bp.route('/health/')
def health_check():
    return jsonify({'status': 'ok'})
