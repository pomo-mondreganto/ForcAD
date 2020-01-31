class FlagSubmitException(Exception):
    """Exception for flag validation"""


class LockedException(Exception):
    """Exception raised when team is locked for rating update"""


class CheckerTimeoutException(Exception):
    """Exception raised by gevent-optimized checkers"""
