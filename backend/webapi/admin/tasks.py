import os

import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sanic.response import json as json_response

import storage
from helplib import models

from .base import make_err_response


class TaskApi:
    def __init__(self, bp):
        bp.add_route(self.list, '/tasks/', methods=['GET'])
        bp.add_route(self.create, '/tasks/', methods=['POST'])
        bp.add_route(self.update, '/tasks/<task_id:int>/', methods=['PUT'])
        bp.add_route(self.delete, '/tasks/<task_id:int>/', methods=['DELETE'])

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
        return json_response(updated.to_dict())

    @staticmethod
    async def delete(_request, task_id):
        await storage.tasks.delete_task(task_id)
        return json_response('ok')
