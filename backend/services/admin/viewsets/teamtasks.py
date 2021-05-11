from flask import request, jsonify

from lib import storage
from .api_base import ApiSet
from .utils import make_err_response


class TeamTaskApi(ApiSet):
    model = 'teamtask'

    @staticmethod
    def list():
        try:
            team_id = int(request.args['team_id'])
            task_id = int(request.args['task_id'])
        except (KeyError, ValueError):
            return make_err_response(
                'Provide team_id and task_id as get params',
                400,
            )

        teamtasks = storage.tasks.get_admin_teamtask_history(
            team_id=team_id,
            task_id=task_id,
        )

        return jsonify(teamtasks)
