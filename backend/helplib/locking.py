from contextlib import contextmanager

import os
from redis.client import Pipeline
from typing import Iterator

from helplib import exceptions


@contextmanager
def acquire_redis_lock(pipeline: Pipeline,
                       name: str,
                       timeout: int = 5000) -> Iterator:
    try:
        while True:
            try:
                nonce = os.urandom(10)
                unlocked = pipeline.set(name, nonce, nx=True, px=timeout)
                if pipeline.transaction:
                    unlocked, = unlocked.execute()  # type: ignore

                if not unlocked:
                    raise exceptions.LockedException
            except exceptions.LockedException:
                continue
            else:
                break

        yield True
    finally:
        res = pipeline.delete(name)
        if pipeline.transaction:
            res.execute()
