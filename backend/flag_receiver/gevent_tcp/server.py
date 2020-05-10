import gevent.monkey

gevent.monkey.patch_all()

import os
import sys
import gevent.pool
import gevent.server

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__),
        ),
    ),
)
sys.path.insert(0, BASE_DIR)

import storage
import logging
from helplib import exceptions

OK_SUBMITS = 0
BAD_SUBMITS = 0
CONNECTIONS = 0

logger = logging.getLogger('gevent_flag_receiver')

logFormatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)


def log_routine():
    was_ok = OK_SUBMITS
    was_bad = BAD_SUBMITS
    was_conn = CONNECTIONS
    while True:
        new_ok, new_bad, new_conn = OK_SUBMITS, BAD_SUBMITS, CONNECTIONS
        logger.info(
            f"OK: {new_ok - was_ok:>6}, BAD: {new_bad - was_bad:>6}, "
            f"CONN: {new_conn - was_conn}, "
            f"TOTOK: {new_ok:>6}, TOTBAD: {new_bad:>6}, "
            f"TOTCONN: {new_conn:>6}"
        )
        was_ok, was_bad, was_conn = new_ok, new_bad, new_conn
        gevent.sleep(5)


def handle(socket, address):
    global OK_SUBMITS, BAD_SUBMITS, CONNECTIONS

    CONNECTIONS += 1

    logger.debug(f'Accepted connection from {address}')

    socket.sendall(b'Welcome! Please, enter your team token:\n')
    rfile = socket.makefile(mode='rb')

    token = rfile.readline()
    try:
        token = token.decode().strip()
    except UnicodeDecodeError:
        logger.debug(f'Could not decode token from {address}: {token}')
        socket.sendall(b'Invalid team token\n')
        rfile.close()
        return

    team_id = storage.teams.get_team_id_by_token(token)

    if not team_id:
        logger.debug(f'Bad token from {address}: {token}')
        socket.sendall(b'Invalid team token\n')
        rfile.close()
        return

    socket.sendall(b'Now enter your flags, one in a line:\n')

    while True:
        flag_data = rfile.readline()
        if not flag_data:
            logger.debug(f'Client {address} disconnected')
            break

        try:
            flag_str = flag_data.decode().strip()
        except UnicodeDecodeError:
            logger.debug(f'Could not decode flag from {address}')
            socket.sendall(b'Invalid flag\n')
            continue

        round = storage.game.get_real_round()

        if round == -1:
            socket.sendall(b'Game is unavailable\n')

        try:
            attacker_delta = storage.game.handle_attack(
                attacker_id=team_id,
                flag_str=flag_str,
                round=round,
            )
        except exceptions.FlagSubmitException as e:
            BAD_SUBMITS += 1
            logger.debug(f'Invalid flag from {address}: {e}')
            socket.sendall(str(e).encode() + b'\n')
        else:
            OK_SUBMITS += 1
            logger.debug(f'Good flag from {address}: {attacker_delta}')
            socket.sendall(
                f'Flag accepted! Earned {attacker_delta} '
                f'flag points!\n'.encode()
            )


if __name__ == '__main__':
    pool = gevent.pool.Pool(10000)
    pool.spawn(log_routine)
    server = gevent.server.StreamServer(('0.0.0.0', 31337), handle, spawn=pool)
    server.serve_forever()
