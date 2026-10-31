from mas.behavior_agent import BehaviorAgent
from objectives.binary import binary_utility


class BinaryAgent(BehaviorAgent):
    def __init__(self, data, probability_file, k, rng, duplicate_limit):
        super().__init__("A1", binary_utility, data, probability_file, k, rng, duplicate_limit)