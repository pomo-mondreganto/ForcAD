import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

import select
import socket
import queue
from typing import Tuple, ByteString, Optional

import storage
import helpers
from helpers import exceptions

BACKLOG = 5
MAX_BUFFER_SIZE = 1000


class SocketServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.inputs = []
        self.outputs = []
        self.message_queues = {}
        self.client_states = {}
        self.buffers = {}

    @staticmethod
    def read_string(sock) -> Tuple[Optional[str], bool]:
        try:
            data = sock.recv(128).decode()
            if not data:
                raise ValueError
        except (ValueError, UnicodeDecodeError, ConnectionResetError):
            return None, False
        return data, True

    def clear(self, sock):
        del self.message_queues[sock]
        del self.client_states[sock]
        del self.buffers[sock]
        sock.close()
        if sock in self.inputs:
            self.inputs.remove(sock)
        if sock in self.outputs:
            self.outputs.remove(sock)

    def write_to_sock(self, sock, message: ByteString):
        if sock not in self.outputs:
            self.outputs.append(sock)
        self.message_queues[sock].put(message)

    def set_sock_break(self, sock):
        self.client_states[sock]['break'] = True

    def get_sock_break(self, sock) -> Optional[bool]:
        return self.client_states[sock].get('break')

    def set_sock_team(self, sock, team_value: bool):
        self.client_states[sock]['team'] = team_value

    def set_sock_team_id(self, sock, team_id: int):
        self.client_states[sock]['team_id'] = team_id

    def get_sock_team_id(self, sock) -> Optional[int]:
        return self.client_states[sock].get('team_id')

    def handle_string(self, sock, string: str):
        team_initialized = self.client_states[sock]['team']

        if not team_initialized:
            team_token = string

            team_id = storage.teams.get_team_id_by_token(team_token)
            if not team_id:
                self.write_to_sock(sock, b'Invalid team token\n')
                self.set_sock_break(sock)
                return

            self.write_to_sock(sock, b'Now enter your flags, one in a line:\n')
            self.set_sock_team(sock, True)
            self.set_sock_team_id(sock, team_id)
        else:
            flag_str = string

            round = storage.game.get_real_round()
            if round == -1:
                self.write_to_sock(sock, b'Game is unavailable\n')
                self.set_sock_break(sock)
                return

            team_id = self.get_sock_team_id(sock)
            try:
                flag = helpers.flags.check_flag(flag_str=flag_str, attacker=team_id, round=round)
            except exceptions.FlagSubmitException as e:
                self.write_to_sock(sock, str(e).encode() + b'\n')
            else:
                storage.flags.add_stolen_flag(flag=flag, attacker=team_id)
                attacker_delta = storage.teams.handle_attack(
                    attacker_id=team_id,
                    victim_id=flag.team_id,
                    task_id=flag.task_id,
                    round=round,
                )
                self.write_to_sock(sock, f'Flag accepted! Earned {attacker_delta} flag points!\n'.encode())

    def serve_forever(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.setblocking(False)

        listen_socket.bind((self.host, self.port))
        listen_socket.listen(BACKLOG)

        print(f'Started TCP server on port {self.port}')

        self.inputs.append(listen_socket)

        while self.inputs:
            readable, writable, exceptional = select.select(
                self.inputs,
                self.outputs,
                self.inputs,
            )

            for sock in readable:
                if sock is listen_socket:
                    conn, addr = sock.accept()

                    print('Accepted connection from:', addr)

                    conn.setblocking(False)
                    self.inputs.append(conn)
                    self.outputs.append(conn)
                    self.message_queues[conn] = queue.Queue()
                    self.client_states[conn] = {}
                    self.buffers[conn] = ''

                    self.write_to_sock(conn, b'Welcome! Please, enter your team token:\n')
                    self.set_sock_team(conn, False)
                elif self.get_sock_break(sock):
                    continue
                else:
                    new_data, ok = self.read_string(sock)
                    if not ok:
                        self.clear(sock)
                        continue

                    self.buffers[sock] += new_data

                    position = self.buffers[sock].find('\n')
                    while position != -1:
                        data = self.buffers[sock][:position]
                        self.handle_string(sock, data)

                        self.buffers[sock] = self.buffers[sock][position + 1:]
                        position = self.buffers[sock].find('\n')

                    if len(self.buffers[sock]) > MAX_BUFFER_SIZE:
                        self.handle_string(sock, self.buffers[sock])
                        self.buffers[sock] = ''

            for sock in writable:
                try:
                    next_msg = self.message_queues[sock].get_nowait()
                except queue.Empty:
                    self.outputs.remove(sock)
                else:
                    sock.send(next_msg)
                finally:
                    if self.get_sock_break(sock):
                        self.clear(sock)

            for sock in exceptional:
                self.clear(sock)


def main():
    host = '0.0.0.0'
    port = 31337

    server = SocketServer(host, port)
    server.serve_forever()


if __name__ == '__main__':
    main()
