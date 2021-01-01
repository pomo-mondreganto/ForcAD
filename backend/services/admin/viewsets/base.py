from sanic import Blueprint
from sanic.response import json as json_response

admin_bp = Blueprint('admin_api')


def make_err_response(err, status=400):
    return json_response({'error': err}, status=status)
