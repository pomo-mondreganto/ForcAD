from cProfile import label
from prometheus_client import Counter

flag_submissions = Counter(
    'flag_submissions_total',
    documentation='Flag submission counter',
    labelnames=[
        'attacker_id',
        'attacker_name',
        'victim_id',
        'victim_name',
        'task_id',
        'task_name',
        'status',
    ],
    namespace='forcad',
    subsystem='http_receiver',
)

flag_points_gained = Counter(
    'flag_points_gained_total',
    documentation='Flag points acquired for attacks',
    labelnames=[
        'attacker_id',
        'attacker_name',
        'victim_id',
        'victim_name',
        'task_id',
        'task_name',
    ],
    namespace='forcad',
    subsystem='http_receiver',
)

flag_points_lost = Counter(
    'flag_points_lost_total',
    documentation='Flag points lost',
    labelnames=[
        'attacker_id',
        'attacker_name',
        'victim_id',
        'victim_name',
        'task_id',
        'task_name',
    ],
    namespace='forcad',
    subsystem='http_receiver',
)
