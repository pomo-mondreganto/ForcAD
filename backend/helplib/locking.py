import os
from contextlib import contextmanager

from helplib import exceptions


@contextmanager
def acquire_redis_lock(pipeline, name, timeout=5000):
    try:
        while True:
            try:
                nonce = os.urandom(10)
                unlocked = pipeline.set(name, nonce, nx=True, px=timeout)
                if pipeline.transaction:
                    unlocked, = unlocked.execute()

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
