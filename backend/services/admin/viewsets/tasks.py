from flask import request, jsonify

from lib import models, storage
from lib.helpers import events
from .api_base import ApiSet
from .utils import make_err_response


class TaskApi(ApiSet):
    model = 'task'

    @staticmethod
    def retrieve(task_id):
        tasks = storage.tasks.get_all_tasks()
        try:
            task = next(filter(lambda x: x.id == task_id, tasks))
        except StopIteration:
            return make_err_response('No such task', status=404)

        return jsonify(task.to_dict())

    @staticmethod
    def list():
        tasks = storage.tasks.get_all_tasks()
        dumped = [task.to_dict() for task in tasks]
        return jsonify(dumped)

    @staticmethod
    def create():
        try:
            data = request.json
            task = models.Task.from_dict(data)
        except TypeError as e:
            return make_err_response(f'Invalid task data: {e}')

        created = storage.tasks.create_task(task)
        events.init_scoreboard()
        return jsonify(created.to_dict()), 201

    @staticmethod
    def update(task_id):
        try:
            data = request.json
            data['id'] = task_id
            task = models.Task.from_dict(request.json)
        except TypeError as e:
            return make_err_response(f'Invalid task data: {e}')

        updated = storage.tasks.update_task(task)
        events.init_scoreboard()
        return jsonify(updated.to_dict())

    @staticmethod
    def destroy(task_id):
        storage.tasks.delete_task(task_id)
        events.init_scoreboard()
        return jsonify('ok')
