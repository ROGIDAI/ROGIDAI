from math import comb, isfinite
from pathlib import Path

from mas.messages import REQUEST, PROPOSE, INFORM, create_message


class BehaviorAgent:
    def __init__(self, agent_id, evaluator, data, probability_file, k, rng, duplicate_limit):
        self.agent_id = agent_id
        self.evaluator = evaluator
        self.data = data
        self.k = k
        self.rng = rng
        self.duplicate_limit = duplicate_limit

        rows = [line.split() for line in Path(probability_file).read_text().splitlines() if line.strip()]
        self.candidates = [int(row[0]) for row in rows]
        self.weights = [float(row[1]) for row in rows]

        if sorted(self.candidates) != list(range(data.qualities.size)):
            raise ValueError(f"Invalid candidate IDs in {probability_file}")
        if any(not isfinite(w) or w < 0 for w in self.weights):
            raise ValueError(f"Invalid probabilities in {probability_file}")
        if not 1 <= k <= sum(w > 0 for w in self.weights):
            raise ValueError(f"Invalid K={k} for {probability_file}")
        if duplicate_limit is not None and duplicate_limit < 0:
            raise ValueError("Duplicate limit must be nonnegative or None")

        self.eligible = [c for c, w in zip(self.candidates, self.weights) if w > 0]
        self.proposed = set()
        self.generated_count = 0
        self.local_duplicate_count = 0
        self.unique_proposal_count = 0
        self.fallback_activations = 0
        self.fallback_generated = 0
        self.fallback_duplicates = 0
        self.evaluation_count = 0
        self.active = True

    def _roulette(self, weights):
        draw = self.rng.uniform(0, sum(weights))
        cumulative = 0.0
        for i, weight in enumerate(weights):
            cumulative += weight
            if draw <= cumulative:
                return i
        return len(weights) - 1

    def propose(self):
        if not self.active or len(self.proposed) >= comb(len(self.eligible), self.k):
            return None

        duplicates = 0
        fallback_used = False

        while True:
            use_uniform = self.duplicate_limit is not None and duplicates >= self.duplicate_limit

            if use_uniform:
                if not fallback_used:
                    self.fallback_activations += 1
                    fallback_used = True
                solution = tuple(sorted(self.rng.sample(self.eligible, self.k)))
                self.fallback_generated += 1
            else:
                weights = self.weights.copy()
                selected = []
                for _ in range(self.k):
                    index = self._roulette(weights)
                    selected.append(self.candidates[index])
                    weights[index] = 0.0
                solution = tuple(sorted(selected))

            self.generated_count += 1
            if solution in self.proposed:
                duplicates += 1
                self.local_duplicate_count += 1
                if use_uniform:
                    self.fallback_duplicates += 1
                continue

            self.proposed.add(solution)
            self.unique_proposal_count += 1
            return solution

    def handle_message(self, message):
        if message["receiver"] != self.agent_id or not self.active:
            return None

        content = message["content"]
        performative = message["performative"]

        if performative == REQUEST and content["type"] == "PROPOSAL_REQUEST":
            solution = self.propose()
            if solution is None:
                return None
            reply = PROPOSE
            result = {"solution": solution}

        elif performative == REQUEST and content["type"] == "EVALUATION_REQUEST":
            solutions = content["solution_set"]
            result = {"utilities": {s: float(self.evaluator(s, self.data)) for s in solutions}}
            self.evaluation_count += len(solutions)
            reply = INFORM

        elif performative == INFORM and content["type"] == "TERMINATION":
            self.active = False
            return None
        else:
            return None

        return create_message(
            reply, self.agent_id, message["sender"], message["conversation_id"],
            content=result, in_reply_to=message.get("reply_with"),
        )

    def statistics(self):
        return {
            "generated": self.generated_count,
            "local_duplicates": self.local_duplicate_count,
            "unique_proposals": self.unique_proposal_count,
            "fallback_activations": self.fallback_activations,
            "fallback_generated": self.fallback_generated,
            "fallback_duplicates": self.fallback_duplicates,
            "objective_evaluations": self.evaluation_count,
        }