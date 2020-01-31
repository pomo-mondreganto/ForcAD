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
