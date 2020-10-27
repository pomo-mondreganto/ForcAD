import asyncio
from sanic import Sanic, Blueprint
from sanic_cors import CORS

from viewsets import admin_bp

app = Sanic('forcad_admin')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

loop = asyncio.get_event_loop()

bps = Blueprint.group(admin_bp, url_prefix='/api/admin')
app.blueprint(bps)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
