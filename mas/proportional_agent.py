from mas.behavior_agent import BehaviorAgent
from objectives.proportional import proportional_utility


class ProportionalAgent(BehaviorAgent):
    def __init__(self, data, probability_file, k, rng, duplicate_limit):
        super().__init__("A2", proportional_utility, data, probability_file, k, rng, duplicate_limit)