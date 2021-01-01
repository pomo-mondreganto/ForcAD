class FlagSubmitException(Exception):
    """Exception for flag validation."""


class CheckerTimeoutException(BaseException):
    """Exception raised by gevent-optimized checkers."""
