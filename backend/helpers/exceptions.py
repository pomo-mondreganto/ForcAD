class FlagSubmitException(Exception):
    """Exception for flag validation"""
    pass


class LockedException(Exception):
    """Exception raised when team is locked for rating update"""
