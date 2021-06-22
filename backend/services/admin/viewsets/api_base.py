from typing import Mapping

from flask import Blueprint, request

from .authentication import check_session
from .utils import abort_with_error


class ApiSet:
    model: str = None

    def get_id_kwarg(self) -> str:
        return f'{self.model}_id'

    def __init__(self, bp: Blueprint, auth: bool = False):
        if self.model is None:
            raise AssertionError(f'{self.__class__.__name__}.model must be defined')

        bp.add_url_rule(
            f'/{self.model}s/',
            endpoint=f'{self.model}_common',
            view_func=self.Dispatch(self),
            methods=['GET', 'POST'],
        )
        bp.add_url_rule(
            f'/{self.model}s/<int:{self.get_id_kwarg()}>/',
            endpoint=f'{self.model}_detail',
            view_func=self.Dispatch(self),
            methods=['GET', 'PUT', 'DELETE'],
        )

        self.kwargs: Mapping = {}
        self.auth = auth

    def _try_call(self, func):
        if not hasattr(self, func):
            abort_with_error('No such page', 404)
        return getattr(self, func)(**self.kwargs)

    def get(self):
        if self.get_id_kwarg() in self.kwargs:
            return self._try_call('retrieve')
        return self._try_call('list')

    def post(self):
        return self._try_call('create')

    def put(self):
        if self.get_id_kwarg() not in self.kwargs:
            abort_with_error('No id provided')
        return self._try_call('update')

    def delete(self):
        if self.get_id_kwarg() not in self.kwargs:
            abort_with_error('No id provided')
        return self._try_call('destroy')

    class Dispatch:
        """Functor to provide method & auth validation for the viewset."""

        def __init__(self, base):
            self.base = base
            self.__name__ = f'{base.__class__.__name__}_Dispatch'

        def __call__(self, *args, **kwargs):
            if self.base.auth:
                check_session()

            req_name = request.method.lower()
            if not hasattr(self.base, req_name):
                abort_with_error('Method not allowed', 405)

            self.base.kwargs = kwargs
            return getattr(self.base, req_name)()
