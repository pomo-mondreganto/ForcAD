from flask import Flask
from flask_cors import CORS

from viewsets import admin_bp

app = Flask('forcad_admin')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

app.register_blueprint(admin_bp, url_prefix='/api/admin/')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
