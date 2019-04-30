import enum


class TaskStatus(enum.Enum):
    """Task status codes Enum"""
    UP = 101
    MUMBLE = 102
    CORRUPT = 103
    DOWN = 104
    CHECK_FAILED = -1337
