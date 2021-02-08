import time


def wait_rounds(rounds):
    round_time = 20
    print(f'Waiting for {round_time * rounds}s')
    time.sleep(rounds * round_time)
