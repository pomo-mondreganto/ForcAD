from lib import storage


async def init_scoreboard_async(sid=None):
    sio = storage.utils.get_async_sio_manager()
    scoreboard = await storage.game.construct_scoreboard()

    await sio.emit(
        'init_scoreboard',
        {'data': scoreboard},
        namespace='/game_events',
        room=sid,
    )
