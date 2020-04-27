import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sanic.response import json as json_response

import storage

from .base import make_err_response
from .api_base import ApiSet


class TeamTaskApi(ApiSet):
    model = 'teamtask'

    @staticmethod
    async def list(request):

        try:
            team_id = int(request.args['team_id'][0])
            task_id = int(request.args['task_id'][0])
        except (KeyError, ValueError):
            return make_err_response(
                'Provide team_id and task_id as get params',
                400,
            )

        teamtasks = await storage.tasks.get_admin_teamtask_history(
            team_id=team_id,
            task_id=task_id,
        )

        return json_response(teamtasks)
