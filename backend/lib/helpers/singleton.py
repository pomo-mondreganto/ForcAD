import json
from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Dict, Any

T = TypeVar('T')


class Singleton(Generic[T], metaclass=ABCMeta):
    """Generic singleton pattern implementation."""
    _values: Dict[str, T] = {}

    @classmethod
    def __get_key(cls, data: Dict[str, Any]):
        rep = json.dumps(data, sort_keys=True)
        return f'{cls.__module__}.{cls.__name__}-{rep}'

    @staticmethod
    @abstractmethod
    def create(**kwargs) -> T:
        """This method must be overloaded to generate the instance."""

    @classmethod
    def get(cls, **kwargs) -> T:
        """This method is the getter of the instance."""
        key = cls.__get_key(kwargs)
        if key not in cls._values:
            cls._values[key] = cls.create(**kwargs)
        return cls._values[key]
