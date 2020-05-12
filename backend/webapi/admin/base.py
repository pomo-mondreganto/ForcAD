import sys
from pathlib import Path

BASE_DIR = Path(__file__).absolute().resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from sanic import Blueprint
from sanic.response import json as json_response

admin_bp = Blueprint('admin_api', url_prefix='/admin')


def make_err_response(err, status=400):
    return json_response({'error': err}, status=status)
