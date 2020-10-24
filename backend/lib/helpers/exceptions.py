class FlagSubmitException(Exception):
    """Exception for flag validation"""


class LockedException(Exception):
    """Exception raised by redis distributed lock"""


class CheckerTimeoutException(BaseException):
    """Exception raised by gevent-optimized checkers"""
