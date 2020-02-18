import enum


class TaskStatus(enum.Enum):
    """Task status codes Enum"""
    UP = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    CHECK_FAILED = 110

    def __str__(self):
        return self.name

    @property
    def counter(self):
        return self.value


class Action(enum.Enum):
    """Checker action Enum"""
    CHECK = 0
    PUT = 1
    GET = 2

    def __str__(self):
        return self.name

    @property
    def counter(self):
        return self.value
