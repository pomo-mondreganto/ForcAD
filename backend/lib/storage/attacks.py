from lib import models, storage
from lib.helpers import exceptions
from lib.storage import utils


def get_attack_data() -> str:
    """Get public flag ids for tasks that provide them, as json string."""
    with utils.get_redis_storage().pipeline(transaction=False) as pipe:
        attack_data, = pipe.get('attack_data').execute()
    return attack_data or 'null'


def handle_attack(attacker_id: int,
                  flag_str: str,
                  current_round: int) -> models.AttackResult:
    """
    Main routine for attack validation & state change.

    Checks flag, locks team for update, calls rating recalculation,
    then publishes redis message about stolen flag.

    :param attacker_id: id of the attacking team
    :param flag_str: flag to be checked
    :param current_round: round of the attack

    :return: attacker rating change
    """

    result = models.AttackResult(attacker_id=attacker_id)

    try:
        flag = storage.flags.get_flag_by_str(flag_str=flag_str,
                                             current_round=current_round)
        result.victim_id = flag.team_id
        result.task_id = flag.task_id
        storage.flags.try_add_stolen_flag(flag=flag, attacker=attacker_id,
                                          current_round=current_round)
        result.submit_ok = True

        with utils.db_cursor() as (conn, curs):
            curs.callproc(
                "recalculate_rating",
                (
                    attacker_id,
                    flag.team_id,
                    flag.task_id,
                    flag.id,
                ),
            )
            attacker_delta, victim_delta = curs.fetchone()
            conn.commit()

        result.attacker_delta = attacker_delta
        result.victim_delta = victim_delta
        result.message = f'Flag accepted! Earned {attacker_delta} flag points!'

        flag_data = {
            'attacker_id': attacker_id,
            'victim_id': flag.team_id,
            'task_id': flag.task_id,
            'attacker_delta': attacker_delta,
            'victim_delta': victim_delta,
        }

        utils.get_wro_sio_manager().emit(
            event='flag_stolen',
            data={'data': flag_data},
            namespace='/live_events',
        )

    except exceptions.FlagSubmitException as e:
        result.message = str(e)

    return result
