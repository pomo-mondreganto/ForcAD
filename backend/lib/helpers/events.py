from lib import storage


def init_scoreboard(sid=None):
    scoreboard = storage.game.construct_scoreboard()
    storage.utils.SIOManager.write_only().emit(
        'init_scoreboard',
        {'data': scoreboard},
        namespace='/game_events',
        room=sid,
    )
