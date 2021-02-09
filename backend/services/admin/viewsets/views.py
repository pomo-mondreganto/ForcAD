from flask import Blueprint, jsonify

admin_bp = Blueprint('admin_api', __name__)


@admin_bp.route('/health/')
def health_check():
    return jsonify({'status': 'ok'})
