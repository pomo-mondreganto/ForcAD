import gevent.monkey

gevent.monkey.patch_all()

import logging
import gevent.pool
import gevent.server

from lib import storage
from lib.monitoring.flag_receiver import SubmitMonitor


class SubmitHandler:
    def __init__(self, logger, monitor: SubmitMonitor):
        self._logger = logger
        self._monitor = monitor

    def _run_loop(self, address, socket, rfile):
        token = rfile.readline()
        try:
            token = token.decode().strip()
        except UnicodeDecodeError:
            self._logger.debug(f'Could not decode token from {address}')
            socket.sendall(b'Invalid team token\n')
            return

        team_id = storage.teams.get_team_id_by_token(token)

        if not team_id:
            self._logger.debug(f'Bad token from {address}')
            socket.sendall(b'Invalid team token\n')
            return

        socket.sendall(b'Now enter your flags, one in a line:\n')

        while True:
            flag_data = rfile.readline()
            if not flag_data:
                self._logger.debug(f'Client {address} disconnected')
                break

            try:
                flag_str = flag_data.decode().strip()
            except UnicodeDecodeError:
                self._logger.debug(f'Could not decode flag from {address}')
                socket.sendall(b'Invalid flag\n')
                continue

            current_round = storage.game.get_real_round()

            if current_round == -1:
                socket.sendall(b'Game is unavailable\n')

            ar = storage.attacks.handle_attack(attacker_id=team_id,
                                               flag_str=flag_str,
                                               current_round=current_round)
            self._monitor.add(ar)
            if ar.submit_ok:
                self._monitor.inc_ok()
                self._logger.debug(
                    f'Good flag from {address}: '
                    f'{ar.attacker_delta}',
                )
            else:
                self._monitor.inc_bad()
                self._logger.debug(
                    f'Invalid flag from {address}: {ar.message}',
                )

            socket.sendall(ar.message.encode() + b'\n')
            gevent.sleep(0)  # handle some other flag

    def __call__(self, socket, address):
        self._logger.debug(f'Accepted connection from {address}')
        self._monitor.inc_conns()

        try:
            socket.sendall(b'Welcome! Please, enter your team token:\n')
        except ConnectionResetError:
            self._logger.warning(f'{address} might be spamming')
            socket.close()
            return

        rfile = socket.makefile(mode='rb')

        try:
            self._run_loop(address, socket, rfile)
        except ConnectionResetError:
            self._logger.warning(f'Connection reset with {address}')
        finally:
            rfile.close()


if __name__ == '__main__':
    receiver_logger = logging.getLogger('gevent_flag_receiver')

    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    receiver_logger.addHandler(console_handler)
    receiver_logger.setLevel(logging.INFO)

    submit_monitor = SubmitMonitor(receiver_logger)
    handler = SubmitHandler(logger=receiver_logger, monitor=submit_monitor)

    pool = gevent.pool.Pool(2000)
    pool.spawn(submit_monitor)
    server = gevent.server.StreamServer(
        ('0.0.0.0', 31337),
        handler,
        spawn=pool,
    )
    server.serve_forever()
