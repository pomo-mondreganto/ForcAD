from lib import models, storage
from lib.helpers import exceptions
from lib.helpers.exceptions import FlagExceptionEnum
from lib.storage import utils, game
from lib.storage.keys import CacheKeys


def get_attack_data() -> str:
    """Get public flag ids for tasks that provide them, as json string."""
    with utils.redis_pipeline(transaction=False) as pipe:
        attack_data, = pipe.get(CacheKeys.attack_data()).execute()
    return attack_data or 'null'


def handle_attack(
        attacker_id: int, flag_str: str, current_round: int
) -> models.AttackResult:
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
        if current_round == -1:
            raise FlagExceptionEnum.GAME_NOT_AVAILABLE

        flag = storage.flags.get_flag_by_str(
            flag_str=flag_str,
            current_round=current_round,
        )
        if flag is None:
            raise FlagExceptionEnum.FLAG_INVALID
        if flag.team_id == attacker_id:
            raise FlagExceptionEnum.FLAG_YOUR_OWN

        game_config = game.get_current_game_config()
        if current_round - flag.round > game_config.flag_lifetime:
            raise FlagExceptionEnum.FLAG_TOO_OLD

        result.victim_id = flag.team_id
        result.task_id = flag.task_id
        success = storage.flags.try_add_stolen_flag(
            flag=flag,
            attacker=attacker_id,
            current_round=current_round,
        )
        if not success:
            raise FlagExceptionEnum.FLAG_YOUR_OWN

    except exceptions.FlagSubmitException as e:
        result.submit_ok = False
        result.message = str(e)

    else:
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

    return result
