import math
from typing import Tuple, Optional


class RatingSystem:
    attacker: float  # attacker score
    victim: float  # victim score
    EPS: float = 1e-7
    game_hardness: float  # the higher the harder
    inflation: bool  # get fp for teams with 0 score

    def __get_probability(self, a: float, b: float) -> float:
        """Probability that player with rating 'a' beats player with rating 'b'"""
        return 1.0 / (1.0 + math.pow(10.0, (b - a) / self.game_hardness))

    def __normalize(self, delta: float) -> float:
        """Smooth out and normalize deltas"""
        L = delta / (math.log(abs(delta) + 1) + self.EPS)
        N = math.log(abs(L) + self.EPS) / (math.log(abs(L) + 1) + self.EPS)
        return math.copysign(L * N, delta)

    @staticmethod
    def __get_geometrical_mean(a: float, b: float) -> float:
        """Get geometrical mean of two numbers"""
        return math.sqrt(a * b)

    def __init__(self,
                 attacker: float,
                 victim: float,
                 game_hardness: Optional[float] = None,
                 inflation: Optional[bool] = None):
        self.attacker = attacker
        self.victim = victim

        if game_hardness is None:
            self.game_hardness = 1300.0
        else:
            self.game_hardness = game_hardness

        if inflation is None:
            self.inflation = False
        else:
            self.inflation = inflation

    def __get_seed(self, rating: float, player_rating: float) -> float:
        """Get player's expected place"""
        ret = 1

        ret += self.__get_probability(self.attacker, rating)
        ret += self.__get_probability(self.victim, rating)

        ret -= self.__get_probability(rating, player_rating)

        return ret

    def __get_satisfaction(self, need_place: float, player_rating: float) -> float:
        """Find such rating that played'd get the needed place

            :param need_place: needed place for player
            :param player_rating: current player rating
            :return: rating that player needs to get need_place
        """
        left = 0
        right = 100000
        for iteration in range(100):
            mid = (left + right) / 2
            if self.__get_seed(rating=mid, player_rating=player_rating) < need_place:
                right = mid
            else:
                left = mid
        return left

    def __calculate_delta(self, rating: float, place: int) -> float:
        """Calculate base rating change (without normalization)"""
        seed = self.__get_seed(rating=rating, player_rating=rating)
        mean = self.__get_geometrical_mean(seed, place)
        R = self.__get_satisfaction(need_place=mean, player_rating=rating)

        return (R - rating) / 2.0

    def calculate(self) -> Tuple[float, float]:
        """Calculates rating change for the attacker and the victim"""
        attacker_delta = self.__calculate_delta(self.attacker, 1)
        victim_delta = self.__calculate_delta(self.victim, 2)

        if not self.inflation:
            norm = min(abs(attacker_delta), abs(victim_delta))
            attacker_delta = math.copysign(norm, attacker_delta)
            victim_delta = math.copysign(norm, victim_delta)

            suggested_attacker_delta = self.__normalize(attacker_delta)
            suggested_victim_delta = self.__normalize(victim_delta)

            attacker_delta = min(attacker_delta, suggested_attacker_delta)
            victim_delta = max(victim_delta, suggested_victim_delta)
        else:
            sum_deltas = attacker_delta + victim_delta
            dec = sum_deltas / 2.0

            attacker_delta -= dec
            victim_delta -= dec

            attacker_delta = self.__normalize(attacker_delta)
            victim_delta = self.__normalize(victim_delta)

            # we don't want negative rating, as inflation is on
            victim_delta = max(victim_delta, -self.victim)

        return attacker_delta, victim_delta
