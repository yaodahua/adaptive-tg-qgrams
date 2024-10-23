import random
from typing import Any, Dict

import numpy as np
from numpy.random import RandomState


def set_random_seed(
    seed: int, reset_random_gen: bool = False, random_state: Dict[str, Any] = None
) -> None:
    """
    Seed the different random generators.

    :param seed:
    :param using_cuda:
    :param reset_random_gen:
    """
    # Seed python RNG
    random.seed(seed)
    # Seed numpy RNG
    np.random.seed(seed)

    _ = RandomGenerator.get_instance(
        seed=seed, reset_random_gen=reset_random_gen, random_state=random_state
    )


class RandomGenerator:
    __instance: "RandomGenerator" = None

    @staticmethod
    def get_instance(
        seed: int = 0,
        reset_random_gen: bool = False,
        random_state: Dict[str, Any] = None,
    ) -> "RandomGenerator":
        if RandomGenerator.__instance is None and random_state is None:
            RandomGenerator(seed=seed)
        elif RandomGenerator.__instance is None and random_state is not None:
            RandomGenerator(seed=seed, random_state=random_state)
        elif reset_random_gen:
            RandomGenerator.__instance = None
            RandomGenerator(seed=seed)
        return RandomGenerator.__instance

    def __init__(self, seed: int, random_state=None):
        if RandomGenerator.__instance is not None:
            raise Exception("This class is a singleton!")

        self.rnd_state: RandomState = np.random.RandomState(seed=seed)
        if random_state is not None:
            self.rnd_state.set_state(random_state)
        RandomGenerator.__instance = self
