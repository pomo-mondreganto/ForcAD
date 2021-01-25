import logging

from flask import Blueprint
from flask import jsonify, make_response, request

from lib import storage
from lib.flags import SubmitMonitor, Judge

logger = logging.getLogger('forcad_http_receiver.views')

receiver_bp = Blueprint('http_receiver', __name__)
monitor = SubmitMonitor(logger=logger)
judge = Judge(monitor=monitor, logger=logger)


def make_error(message: str, status: int = 400):
    return make_response(jsonify({'error': message}), status)


@receiver_bp.route('/', methods=['PUT'], strict_slashes=False)
def get_teams():
    monitor.inc_conns()

    token = request.headers.get('X-Team-Token', '')
    team_id = storage.teams.get_team_id_by_token(token)
    if not team_id:
        logger.debug('[%s] bad token', request.remote_addr)
        return make_error('Invalid team token.')

    current_round = storage.game.get_real_round()
    if current_round == -1:
        return make_error('Game not started.')

    data = request.get_json(force=True)
    if data is None:
        logger.debug('[%s] sent invalid json', request.remote_addr)
        return make_error('Invalid json sent')
    if not isinstance(data, list) or len(data) > 100:
        logger.debug('[%s] invalid format', request.remote_addr)
        return make_error(
            'Invalid request format. '
            'Must provide a list with no more than 100 flags.'
        )

    attack_results = judge.process_many(team_id, flags=data)

    responses = []
    for ar, flag in zip(attack_results, data):
        logger.debug(
            '[%s] processed flag %s, %s: %s',
            request.remote_addr,
            flag,
            'ok' if ar.submit_ok else 'bad',
            ar.message,
        )

        responses.append(
            {
                'msg': f'[{flag}] {ar.message}',
                'flag': flag,
            }
        )

    return jsonify(responses)


@receiver_bp.route('/health/')
def health_check():
    return jsonify({'status': 'ok'})
