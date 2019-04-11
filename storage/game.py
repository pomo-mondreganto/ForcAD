import storage


def get_current_round() -> int:
    with storage.get_redis_storage().pipeline(transaction=True) as pipeline:
        round, = pipeline.get('round').execute()
    try:
        round = round.decode()
        return int(round)
    except ValueError or AttributeError:
        return -1
