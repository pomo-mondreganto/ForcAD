from sanic import Sanic, Blueprint
from sanic_cors import CORS

from views import client_bp

app = Sanic('forcad_api')
CORS(
    app,
    supports_credentials=True,
    automatic_options=True,
)

bps = Blueprint.group(client_bp, url_prefix='/api/client')
app.blueprint(bps)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
