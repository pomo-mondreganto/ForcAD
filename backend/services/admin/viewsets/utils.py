from flask import Blueprint, jsonify, Response

admin_bp = Blueprint('admin_api', __name__)


def make_err_response(err, status=400):
    return Response(jsonify({'error': err}), status=status)
