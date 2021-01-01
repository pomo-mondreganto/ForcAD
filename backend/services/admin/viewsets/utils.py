from flask import Blueprint, jsonify, make_response, abort

admin_bp = Blueprint('admin_api', __name__)


def make_err_response(err, status=400):
    return make_response(jsonify({'error': err}), status)


def abort_with_error(err, status=400):
    abort(make_err_response(err, status))
