import math
from typing import Tuple


class RatingSystem:
    attacker: float  # attacker score
    victim: float  # victim score
    EPS: float = 1e-7
    game_hardness: float  # the higher the harder

    def __get_probability(self, a: float, b: float) -> float:
        """Probability that player with rating 'a' beats player with rating 'b'"""
        return 1.0 / (1.0 + math.pow(10.0, (b - a) / self.game_hardness))

    def __normalize(self, delta: float) -> float:
        """Smooth out and normalize rating change"""
        L = delta / math.log(abs(delta) + 1)
        N = math.log(abs(L) + self.EPS) / math.log(abs(L) + 1)
        return math.copysign(L * N, delta)

    @staticmethod
    def __get_geometrical_mean(a: float, b: float) -> float:
        """Geometrical mean of two floats"""
        return math.sqrt(a * b)

    def __init__(self, attacker: float, victim: float, game_hardness: float = 1300.0):
        self.attacker = attacker
        self.victim = victim
        self.game_hardness = game_hardness

    def __get_seed(self, rating: float, player_rating: float) -> float:
        """Get player's expected rating"""
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

        sum_deltas = attacker_delta + victim_delta
        dec = sum_deltas / 2.0

        attacker_delta -= dec
        victim_delta -= dec

        attacker_delta = self.__normalize(attacker_delta)
        victim_delta = self.__normalize(victim_delta)

        return attacker_delta, victim_delta
