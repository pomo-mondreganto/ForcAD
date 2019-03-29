import enum


class TaskStatus(enum.Enum):
    UP = 101
    MUMBLE = 102
    CORRUPT = 103
    DOWN = 104
    CHECK_FAILED = -1337
