from enum import Enum

import os
import time
from contextlib import contextmanager
from redis.client import Pipeline
from typing import Iterator


class LockEnum(Enum, str):
    GAME_START = 'game_start_lock'
    ROUND_UPDATE = 'round_update_lock'


@contextmanager
def acquire_redis_lock(pipeline: Pipeline, name: str, timeout: int = 5000) -> Iterator:
    lock_time = None
    try:
        while True:
            nonce = os.urandom(10)
            unlocked, = pipeline.set(
                name,
                nonce,
                nx=True,
                px=timeout,
            ).execute()  # type: ignore

            if unlocked:
                lock_time = time.monotonic()
                break

        yield True
    finally:
        # Lock was acquired and a lot of time left
        # until lock is invalidated, safe to delete
        if lock_time is not None:
            lock_deadline = lock_time + timeout / 1000
            if lock_deadline - time.monotonic() > 0.5:
                pipeline.delete(name).execute()
