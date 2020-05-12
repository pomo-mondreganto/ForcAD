import sys

from pathlib import Path

BASE_DIR = Path(__file__).absolute().resolve().parent
sys.path.insert(0, str(BASE_DIR))

from test_service_lib import *

from gevent import monkey

monkey.patch_all()


class Checker(BaseChecker):
    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(
                Status.DOWN,
                'Connection error',
                'Got requests connection error',
            )

    def check(self):
        self.mch.ping()
        self.cquit(Status.OK)

    def put(self, flag_id, flag, vuln):
        new_id = self.mch.put_flag(flag, vuln)
        self.cquit(Status.OK, new_id)

    def get(self, flag_id, flag, vuln):
        got_flag = self.mch.get_flag(flag_id, vuln)
        assert_eq(got_flag, flag, 'Could not get flag', status=Status.CORRUPT)
        self.cquit(Status.OK)
