import logging

from flask import Blueprint
from flask import jsonify, make_response, request

from lib import storage
from lib.flags import SubmitMonitor, Judge

from metrics import flag_submissions, flag_points_gained, flag_points_lost

logger = logging.getLogger('http_receiver.views')

receiver_bp = Blueprint('http_receiver', __name__)
monitor = SubmitMonitor(logger=logger)
judge = Judge(monitor=monitor, logger=logger)


def make_error(message: str, status: int = 400):
    return make_response(jsonify({'error': message}), status)


@receiver_bp.route('/', methods=['PUT'], strict_slashes=False)
def get_teams():
    monitor.inc_requests()

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

    team_name_by_id = {team.id: team.name for team in storage.teams.get_teams()}
    task_name_by_id = {task.id: task.name for task in storage.tasks.get_tasks()}

    responses = []
    for ar, flag in zip(attack_results, data):
        common_metric_kwargs = dict(
            attacker_id=ar.attacker_id,
            attacker_name=team_name_by_id.get(ar.attacker_id, 'unknown'),
            victim_id=ar.victim_id,
            victim_name=team_name_by_id.get(ar.victim_id, 'unknown'),
            task_id=ar.task_id,
            task_name=task_name_by_id.get(ar.task_id, 'unknown'),
        )
        flag_submissions.labels(
            status='ok' if ar.submit_ok else 'bad',
            **common_metric_kwargs,
        ).inc()
        flag_points_gained.labels(**common_metric_kwargs).inc(ar.attacker_delta)
        flag_points_lost.labels(**common_metric_kwargs).inc(-ar.victim_delta)

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
