"""Simple "viewsets" implementation for models' REST API."""

from .authentication import login, status
from .tasks import TaskApi
from .teams import TeamApi
from .teamtasks import TeamTaskApi
from .views import admin_bp

TeamApi(admin_bp, auth=True)
TaskApi(admin_bp, auth=True)
TeamTaskApi(admin_bp, auth=True)

admin_bp.add_url_rule('/login/', 'login', login, methods=['POST'])
admin_bp.add_url_rule('/status/', 'status', status, methods=['GET'])
