from .base import admin_bp
from .tasks import TaskApi
from .teams import TeamApi

TeamApi(admin_bp)
TaskApi(admin_bp)
