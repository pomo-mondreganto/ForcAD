import json
from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Dict

T = TypeVar('T')


class Singleton(Generic[T], metaclass=ABCMeta):
    """Generic singleton pattern implementation."""
    _values: Dict[str, T] = None

    @staticmethod
    @abstractmethod
    def create(**kwargs) -> T:
        """This method must be overloaded to generate the instance."""

    @classmethod
    def get(cls, **kwargs) -> T:
        """This method is the getter of the instance."""
        rep = json.dumps(kwargs, sort_keys=True)
        if rep not in cls._values:
            cls._values[rep] = cls.create(**kwargs)
        return cls._values[rep]
