import aioredis
import redis
from typing import Callable, Optional, Iterable


def cache_helper(pipeline,
                 cache_key: str,
                 cache_func: Callable,
                 cache_args: Optional[Iterable] = None,
                 cache_kwargs: Optional[dict] = None,
                 on_cached: Optional[Callable] = None,
                 on_cached_args: Optional[Iterable] = None,
                 on_cached_kwargs: Optional[dict] = None):
    if cache_args is None:
        cache_args = tuple()
    if cache_kwargs is None:
        cache_kwargs = dict()
    if on_cached_args is None:
        on_cached_args = tuple()
    if on_cached_kwargs is None:
        on_cached_kwargs = dict()

    was_changed = False
    while True:
        try:
            pipeline.watch(cache_key)
            cached = pipeline.exists(cache_key)

            pipeline.multi()

            if not cached:
                was_changed = True
                cache_func(*cache_args, **cache_kwargs)
            elif on_cached is not None:
                on_cached(*on_cached_args, **on_cached_kwargs)

            pipeline.execute()
        except redis.WatchError:
            continue
        else:
            break

    return was_changed


async def async_cache_helper(
        redis_aio,
        cache_key: str,
        cache_func: Callable,
        cache_args: Optional[Iterable] = None,
        cache_kwargs: Optional[dict] = None):
    if cache_args is None:
        cache_args = tuple()
    if cache_kwargs is None:
        cache_kwargs = dict()

    while True:
        try:
            await redis_aio.watch(cache_key)
            cached = await redis_aio.exists(cache_key)

            tr = redis_aio.multi_exec()
            cache_kwargs['pipeline'] = tr
            if not cached:
                cache_func(*cache_args, **cache_kwargs)

            await tr.execute()
            await redis_aio.unwatch()
        except (aioredis.MultiExecError, aioredis.WatchVariableError):
            continue
        else:
            break
