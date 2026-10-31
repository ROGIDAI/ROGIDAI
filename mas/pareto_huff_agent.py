from mas.behavior_agent import BehaviorAgent
from objectives.pareto_huff import pareto_huff_utility


class ParetoHuffAgent(BehaviorAgent):
    def __init__(self, data, probability_file, k, rng, duplicate_limit):
        super().__init__("A3", pareto_huff_utility, data, probability_file, k, rng, duplicate_limit)