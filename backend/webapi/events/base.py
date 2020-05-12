import sys
from pathlib import Path

BASE_DIR = Path(__file__).absolute().resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import storage
import socketio

sio_manager = storage.get_async_sio_manager()
sio = socketio.AsyncServer(
    async_mode='sanic',
    client_manager=sio_manager,
    cors_allowed_origins=[],
)


async def emit_init_scoreboard(sid=None):
    scoreboard = await storage.game.construct_scoreboard()

    await sio.emit(
        'init_scoreboard',
        {'data': scoreboard},
        namespace='/game_events',
        room=sid,
    )


@sio.on('connect', namespace='/game_events')
async def handle_connect(sid, _environ):
    await emit_init_scoreboard(sid)
