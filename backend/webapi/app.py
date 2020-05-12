import sys

from pathlib import Path

BASE_DIR = Path(__file__).absolute().resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import asyncio

from sanic import Sanic, Blueprint
from sanic_cors import CORS

from webapi.monitoring import MonitorClient
from webapi.client import client_bp
from webapi.admin import admin_bp
from webapi.events import sio

app = Sanic('forcad_api')
app.enable_websocket(True)
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

loop = asyncio.get_event_loop()
mon = MonitorClient(app)
mon.add_endpoint('/api/metrics')
loop.run_until_complete(mon.connect_consumer())

sio.attach(app)

bps = Blueprint.group(admin_bp, client_bp, url_prefix='/api')
app.blueprint(bps)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
