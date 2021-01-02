from lib import storage


def init_scoreboard(sid=None):
    sio = storage.utils.get_sio_manager()
    scoreboard = storage.game.construct_scoreboard()

    sio.emit(
        'init_scoreboard',
        {'data': scoreboard},
        namespace='/game_events',
        room=sid,
    )
