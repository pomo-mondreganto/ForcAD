import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sanic.response import json as json_response

import storage
from helplib import models

from webapi.events import emit_init_scoreboard
from .base import make_err_response
from .api_base import ApiSet


class TaskApi(ApiSet):
    model = 'task'

    @staticmethod
    async def list(_request):
        tasks = await storage.tasks.get_all_tasks_async()
        dumped = [task.to_dict() for task in tasks]
        return json_response(dumped)

    @staticmethod
    async def create(request):
        try:
            data = request.json
            task = models.Task.from_dict(data)
        except TypeError as e:
            return make_err_response(f'Invalid task data: {e}')

        created = await storage.tasks.create_task(task)
        await emit_init_scoreboard()
        return json_response(created.to_dict(), status=201)

    @staticmethod
    async def update(request, task_id):
        try:
            data = request.json
            data['id'] = task_id
            task = models.Task.from_dict(request.json)
        except TypeError as e:
            return make_err_response(f'Invalid task data: {e}')

        updated = await storage.tasks.update_task(task)
        await emit_init_scoreboard()
        return json_response(updated.to_dict())
