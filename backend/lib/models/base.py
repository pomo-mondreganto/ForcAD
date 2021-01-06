import yaml
from kombu.utils import json as kjson
from typing import List, Dict, Any, Tuple, TypeVar, Type, TextIO

# noinspection PyTypeChecker
T = TypeVar('T', bound='BaseModel')


# noinspection SqlResolve
class BaseModel:
    """Generic model implementing basic methods to load and print"""

    __slots__: Tuple[str, ...] = ()
    table_name = 'undefined'
    defaults: Dict[str, Any] = {}

    @property
    def model_name(self) -> str:
        return self.__class__.__name__

    def __init__(self, **kwargs: Any):
        for attr in self.__slots__:
            if attr == 'id':
                setattr(self, attr, kwargs.get(attr))
                continue
            if attr not in kwargs:
                if attr not in self.defaults:
                    raise KeyError(
                        f'Attribute {attr} is required for model {self.model_name}'
                    )
                setattr(self, attr, self.defaults[attr])
            else:
                setattr(self, attr, kwargs[attr])

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        d = kjson.loads(json_str)
        return cls(**d)

    @classmethod
    def from_yaml(cls: Type[T], yaml_obj: TextIO) -> T:
        d = yaml.safe_load(yaml_obj)
        return cls(**d)

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> T:
        return cls(**d)

    def to_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in self.__slots__}

    def to_json(self) -> str:
        return kjson.dumps(self.to_dict())  # type: ignore

    @classmethod
    def _get_column_names(cls) -> List[str]:
        return list(filter(lambda x: x != 'id', cls.__slots__))

    @classmethod
    def get_select_all_query(cls) -> str:
        return f'SELECT * FROM {cls.table_name}'

    @classmethod
    def get_select_one_query(cls) -> str:
        return f'SELECT * FROM {cls.table_name} WHERE id=%(id)s'

    @classmethod
    def get_select_active_query(cls) -> str:
        return f'SELECT * FROM {cls.table_name} WHERE active=TRUE'

    @classmethod
    def get_insert_query(cls) -> str:
        column_names = cls._get_column_names()
        columns = ', '.join(column_names)
        values = ', '.join(f'%({column})s' for column in column_names)
        q = (
            f'INSERT INTO {cls.table_name} ({columns}) '
            f'VALUES ({values}) RETURNING id'
        )
        return q

    @classmethod
    def get_update_query(cls) -> str:
        column_names = cls._get_column_names()
        update_data = ', '.join(f'{column}=%({column})s' for column in column_names)
        return f'UPDATE {cls.table_name} SET {update_data} WHERE id=%(id)s'

    @classmethod
    def get_delete_query(cls) -> str:
        return f'UPDATE {cls.table_name} SET active=FALSE WHERE id=%(id)s'

    def insert(self, curs) -> None:
        curs.execute(self.get_insert_query(), self.to_dict())
        inserted_id, = curs.fetchone()
        setattr(self, 'id', inserted_id)

    def __repr__(self) -> str:
        return str(self)
