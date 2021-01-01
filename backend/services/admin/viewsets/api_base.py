from typing import Mapping

from sanic.exceptions import NotFound, MethodNotSupported

from .authentication import check_session


class ApiSet:
    model: str = None

    def get_id_kwarg(self) -> str:
        return f'{self.model}_id'

    def __init__(self, bp, auth: bool = False):
        if self.model is None:
            raise AssertionError(f'{self.__class__.__name__}.model '
                                 f'must be defined')

        bp.add_route(
            self.Dispatch(self),
            f'/{self.model}s/',
            methods=['GET', 'POST'],
        )
        bp.add_route(
            self.Dispatch(self),
            f'/{self.model}s/<{self.get_id_kwarg()}:int>',
            methods=['PUT', 'DELETE'],
        )

        self.request = None
        self.kwargs: Mapping = {}
        self.auth = auth

    async def _try_call(self, func):
        if not hasattr(self, func):
            raise NotFound('No such page')
        return await getattr(self, func)(self.request, **self.kwargs)

    async def get(self):
        if self.get_id_kwarg() in self.kwargs:
            return await self._try_call('retrieve')
        return await self._try_call('list')

    async def post(self):
        return await self._try_call('create')

    async def put(self):
        if self.get_id_kwarg() not in self.kwargs:
            raise NotFound('No id provided')
        return await self._try_call('update')

    async def delete(self):
        if self.get_id_kwarg() not in self.kwargs:
            raise NotFound('No id provided')
        return await self._try_call('destroy')

    class Dispatch:
        """Functor to provide method & auth validation for the viewset."""

        def __init__(self, base):
            self.base = base
            self.__name__ = f'{base.__class__.__name__}.Dispatch'

        async def __call__(self, request, *args, **kwargs):
            if self.base.auth:
                await check_session(request)

            req_name = request.method.lower()
            if not hasattr(self.base, req_name):
                raise MethodNotSupported(
                    'Method not allowed for url',
                    method=request.method,
                    allowed_methods=['GET', 'POST', 'PUT', 'DELETE'],
                )

            self.base.request = request
            self.base.kwargs = kwargs
            return await getattr(self.base, req_name)()
