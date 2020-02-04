import gevent.monkey

gevent.monkey.patch_all()

import os
import sys
import gevent.pool
import gevent.server

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

import storage
from helplib import exceptions


def handle(socket, address):
    print('Accepted connection from:', address)

    socket.sendall(b'Welcome! Please, enter your team token:\n')
    rfile = socket.makefile(mode='rb')

    token = rfile.readline()
    try:
        token = token.decode().strip()
    except UnicodeDecodeError:
        socket.sendall(b'Invalid team token\n')
        rfile.close()
        return

    team_id = storage.teams.get_team_id_by_token(token)

    if not team_id:
        socket.sendall(b'Invalid team token\n')
        rfile.close()
        return

    socket.sendall(b'Now enter your flags, one in a line:\n')

    while True:
        flag_data = rfile.readline()
        if not flag_data:
            print(f'Client {address} disconnected')
            break

        try:
            flag_str = flag_data.decode().strip()
        except UnicodeDecodeError:
            socket.sendall(b'Invalid flag\n')
            continue

        round = storage.game.get_real_round()

        if round == -1:
            socket.sendall(b'Game is unavailable\n')

        try:
            attacker_delta = storage.teams.handle_attack(
                attacker_id=team_id,
                flag_str=flag_str,
                round=round,
            )
        except exceptions.FlagSubmitException as e:
            socket.sendall(str(e).encode() + b'\n')
        else:
            socket.sendall(f'Flag accepted! Earned {attacker_delta} flag points!\n'.encode())


if __name__ == '__main__':
    pool = gevent.pool.Pool(10000)
    server = gevent.server.StreamServer(('0.0.0.0', 31337), handle, spawn=pool)
    server.serve_forever()
