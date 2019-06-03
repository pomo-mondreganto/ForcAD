class FlagSubmitException(Exception):
    """Exception for flag validation"""
    pass


class TeamLockedException(Exception):
    """Exception raised when team is locked for rating update"""


class GameLockedException(Exception):
    """Exception raised when game config is locked"""
