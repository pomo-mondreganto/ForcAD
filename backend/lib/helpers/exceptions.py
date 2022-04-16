class FlagSubmitException(Exception):
    """Exception for flag validation."""


class FlagExceptionEnum:
    GAME_NOT_AVAILABLE = FlagSubmitException('Game is not available.')
    FLAG_INVALID = FlagSubmitException('Flag is invalid or too old.')
    FLAG_TOO_OLD = FlagSubmitException('Flag is too old')
    FLAG_YOUR_OWN = FlagSubmitException('Flag is your own')
    FLAG_ALREADY_STOLEN = FlagSubmitException('Flag already stolen')
