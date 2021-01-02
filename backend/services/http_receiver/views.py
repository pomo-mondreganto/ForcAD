import eventlet
import logging
from flask import Blueprint
from flask import jsonify, make_response, request

from lib import storage
from lib.flags import SubmitMonitor, Notifier

logger = logging.getLogger('forcad_http_receiver.views')

receiver_bp = Blueprint('http_receiver', __name__)
submit_monitor = SubmitMonitor(logger=logger)
notifier = Notifier(logger=logger)

eventlet.spawn_n(submit_monitor)


def make_error(message: str, status: int = 400):
    return make_response(jsonify({'error': message}), status)


@receiver_bp.route('/', methods=['PUT'], strict_slashes=False)
def get_teams():
    submit_monitor.inc_conns()

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
    results = []
    for flag in data:
        ar = storage.attacks.handle_attack(
            attacker_id=team_id,
            flag_str=flag,
            current_round=current_round,
        )
        logger.debug(
            '[%s] processed flag, %s: %s',
            request.remote_addr,
            'ok' if ar.submit_ok else 'bad',
            ar.message,
        )

        if ar.submit_ok:
            notifier.add(ar)
        submit_monitor.add(ar)

        results.append({'msg': ar.message})

    return jsonify(results)


@receiver_bp.route('/status/')
def health_check():
    logger.debug('status called')
    return jsonify({'status': 'ok'})
