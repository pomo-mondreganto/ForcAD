from functools import wraps
from typing import Union, Tuple, Type

ExceptType = Union[Type[Exception], Tuple[Type[Exception]]]


def ignore_exc_wrapper(exc: ExceptType):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except exc:
                pass

        return wrapper

    return decorator
