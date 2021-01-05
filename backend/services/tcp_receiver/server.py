import eventlet

eventlet.monkey_patch()

import logging
from typing import TextIO

from lib import storage
from lib.flags import SubmitMonitor, Judge


class SubmitHandler:
    def __init__(self,
                 logger: logging.Logger,
                 judge: Judge,
                 monitor: SubmitMonitor):
        self._logger = logger
        self._judge = judge
        self._monitor = monitor

    def _run_loop(self, logger, conn: TextIO):
        try:
            token = conn.readline().strip()
        except UnicodeDecodeError:
            logger.debug('bad token [not decoded]')
            conn.write('Invalid team token\n')
            conn.flush()
            return

        team_id = storage.teams.get_team_id_by_token(token)

        if not team_id:
            logger.debug('bad token [team not found]')
            conn.write('Invalid team token\n')
            conn.flush()
            return

        logger.debug('team %s authorized', team_id)

        conn.write('Now enter your flags, one in a line:\n')
        conn.flush()

        while True:
            try:
                flag_str = conn.readline().strip()
            except UnicodeDecodeError:
                logger.debug('sent junk')
                conn.write('Invalid flag\n')
                conn.flush()
                eventlet.sleep(0)
                continue

            if not flag_str:
                logger.debug('disconnected')
                break

            ar = self._judge.process(team_id, flag_str)
            logger.debug(
                'processed flag, %s: %s',
                'ok' if ar.submit_ok else 'bad', ar.message,
            )

            conn.write(ar.message + '\n')
            conn.flush()
            eventlet.sleep(0)  # handle some other flag

    def __call__(self, socket, address):
        logger = logging.LoggerAdapter(self._logger, {'address': address})
        logger.debug('accepted')
        self._monitor.inc_conns()

        try:
            socket.sendall(b'Welcome! Please, enter your team token:\n')
        except ConnectionResetError:
            logger.warning('might be DOS')
            socket.close()
            return

        conn = socket.makefile(mode='rw')
        try:
            self._run_loop(logger, conn)
        except ConnectionResetError:
            logger.warning('connection reset')
        finally:
            conn.close()
            socket.close()


if __name__ == '__main__':
    receiver_logger = logging.getLogger('tcp_receiver')
    judge_logger = logging.getLogger('tcp_receiver_monitor')

    simple_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
    )
    addr_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(address)s] %(message)s",
    )

    addr_handler = logging.StreamHandler()
    addr_handler.setFormatter(addr_formatter)

    monitor_handler = logging.StreamHandler()
    monitor_handler.setFormatter(simple_formatter)

    receiver_logger.addHandler(addr_handler)
    receiver_logger.setLevel(logging.DEBUG)

    judge_logger.addHandler(monitor_handler)
    judge_logger.setLevel(logging.INFO)

    submit_monitor = SubmitMonitor(judge_logger)
    attack_judge = Judge(monitor=submit_monitor, logger=judge_logger)

    handler = SubmitHandler(
        logger=receiver_logger,
        monitor=submit_monitor,
        judge=attack_judge,
    )

    server = eventlet.listen(('0.0.0.0', 31337))
    pool = eventlet.GreenPool(size=2000)

    while True:
        try:
            sock, addr = server.accept()
            pool.spawn_n(handler, sock, addr)
        except (SystemExit, KeyboardInterrupt):
            break
