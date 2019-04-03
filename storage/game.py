import storage


def get_current_round() -> int:
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        round, = pipeline.get('round').execute()

    return round
