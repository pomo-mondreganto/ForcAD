import math
from typing import Tuple


class RatingSystem:
    attacker: float
    victim: float

    @staticmethod
    def __get_probability(a: float, b: float) -> float:
        return 1.0 / (1.0 + math.pow(10.0, (b - a) / 1300.0))

    @staticmethod
    def __normalize(a: float) -> float:
        return a / math.log(abs(a) + 1)

    @staticmethod
    def __get_geometrical_mean(a: float, b: float) -> float:
        return math.sqrt(a * b)

    def __init__(self, attacker: float, victim: float):
        self.attacker = attacker
        self.victim = victim

    def __get_seed(self, rating: float) -> float:
        ret = 1

        ret += self.__get_probability(self.attacker, rating)
        ret += self.__get_probability(self.victim, rating)

        return ret - 0.5

    def __get_satisfaction(self, s: float) -> float:
        left = 0
        right = 100000
        for iteration in range(300):
            mid = (left + right) / 2
            if self.__get_seed(mid) < s:
                right = mid
            else:
                left = mid
        return left

    def __calculate_delta(self, rating: float, place: int) -> float:
        seed = self.__get_seed(rating)
        mean = self.__get_geometrical_mean(seed, place)
        R = self.__get_satisfaction(mean)

        return (R - rating) / 2.0

    def calculate(self) -> Tuple[float, float]:
        attacker_delta = self.__calculate_delta(self.attacker, 1)
        victim_delta = self.__calculate_delta(self.victim, 2)

        sum_deltas = attacker_delta + victim_delta

        attacker_delta -= sum_deltas / 2.0
        victim_delta -= sum_deltas / 2.0

        attacker_delta = self.__normalize(attacker_delta)
        victim_delta = self.__normalize(victim_delta)

        return attacker_delta, victim_delta
