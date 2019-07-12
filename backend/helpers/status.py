import enum


class TaskStatus(enum.Enum):
    """Task status codes Enum"""
    UP = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    CHECK_FAILED = 110
