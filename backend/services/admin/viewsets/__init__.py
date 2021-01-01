"""Simple "viewsets" implementation for models' REST API."""

from .authentication import login, status
from .base import admin_bp
from .tasks import TaskApi
from .teams import TeamApi
from .teamtasks import TeamTaskApi

TeamApi(admin_bp, auth=True)
TaskApi(admin_bp, auth=True)
TeamTaskApi(admin_bp, auth=True)

admin_bp.add_route(login, '/login/', methods=['POST'])
admin_bp.add_route(status, '/status/', methods=['GET'])
