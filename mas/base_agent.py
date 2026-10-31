from time import perf_counter

from mas.messages import REQUEST, INFORM, PROPOSE, PROTOCOL, create_message


class BaseAgent:
    def __init__(self, agents, max_iters, epsilon=1e-6, verbose=False):
        self.agents = agents
        self.max_iters = max_iters
        self.epsilon = epsilon
        self.verbose = verbose
        self.global_history = set()
        self.archive = []
        self.evaluated = []
        self.global_duplicates = {agent.agent_id: 0 for agent in agents}
        self.proposal_requests = 0
        self.evaluation_requests = 0
        self.completed_iterations = 0
        self.proposal_seconds = 0.0
        self.evaluation_seconds = 0.0
        self.archive_seconds = 0.0
        self.search_seconds = 0.0

    def dominates(self, a, b):
        return (all(x >= y - self.epsilon for x, y in zip(a, b))
                and any(x > y + self.epsilon for x, y in zip(a, b)))

    def update_archive(self, solution, values):
        if any(self.dominates(old_values, values) for _, old_values in self.archive):
            return
        self.archive = [(old_solution, old_values)
                        for old_solution, old_values in self.archive
                        if not self.dominates(values, old_values)]
        self.archive.append((solution, values))

    def request_proposal(self, agent, iteration, current):
        for attempt in range(1, 1001):
            request_id = f"proposal_{iteration}_{agent.agent_id}_{attempt}"
            message = create_message(
                REQUEST, "A0", agent.agent_id, f"iter_{iteration}",
                {"type": "PROPOSAL_REQUEST"}, reply_with=request_id,
            )
            self.proposal_requests += 1
            reply = agent.handle_message(message)

            if reply is None:
                raise RuntimeError(f"{agent.agent_id} cannot generate another proposal")

            if (reply["performative"] != PROPOSE or reply["in_reply_to"] != request_id
                    or reply["sender"] != agent.agent_id or reply["receiver"] != "A0"
                    or reply["protocol"] != PROTOCOL
                    or reply["conversation_id"] != f"iter_{iteration}"):
                raise RuntimeError(f"Invalid proposal reply from {agent.agent_id}")

            solution = tuple(reply["content"]["solution"])

            if solution in current or solution in self.global_history:
                self.global_duplicates[agent.agent_id] += 1
                continue

            return solution

        raise RuntimeError(f"{agent.agent_id} exceeded 1000 global proposal retries")

    def run(self):
        start = perf_counter()

        for iteration in range(self.max_iters):
            conversation_id = f"iter_{iteration}"
            proposals = []
            current = set()

            phase_start = perf_counter()

            for agent in self.agents:
                solution = self.request_proposal(agent, iteration, current)
                proposals.append(solution)
                current.add(solution)

            self.proposal_seconds += perf_counter() - phase_start

            phase_start = perf_counter()
            results = {}

            for agent in self.agents:
                request_id = f"evaluation_{iteration}_{agent.agent_id}"
                message = create_message(
                    REQUEST, "A0", agent.agent_id, conversation_id,
                    {"type": "EVALUATION_REQUEST", "solution_set": proposals},
                    reply_with=request_id,
                )
                self.evaluation_requests += 1
                reply = agent.handle_message(message)

                if (reply is None or reply["performative"] != INFORM
                        or reply["in_reply_to"] != request_id
                        or reply["sender"] != agent.agent_id or reply["receiver"] != "A0"
                        or reply["protocol"] != PROTOCOL
                        or reply["conversation_id"] != conversation_id):
                    raise RuntimeError(f"Invalid evaluation reply from {agent.agent_id}")

                results[agent.agent_id] = reply["content"]["utilities"]

            self.evaluation_seconds += perf_counter() - phase_start

            phase_start = perf_counter()

            for solution in proposals:
                values = tuple(results[agent.agent_id][solution] for agent in self.agents)
                self.evaluated.append((iteration, solution, values))
                self.update_archive(solution, values)

            self.global_history.update(proposals)
            self.archive_seconds += perf_counter() - phase_start
            self.completed_iterations += 1

            if self.verbose and self.completed_iterations % 100 == 0:
                print(f"Iteration {self.completed_iterations:,}/{self.max_iters:,}", flush=True)

        self.search_seconds = perf_counter() - start

        for agent in self.agents:
            message = create_message(
                INFORM, "A0", agent.agent_id, f"iter_{self.max_iters}",
                {"type": "TERMINATION", "reason": "MAX_ITER_REACHED"},
            )
            agent.handle_message(message)

        return self.archive

    def strict_front(self):
        def dominates(a, b):
            return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))

        front = []

        for _, solution, values in self.evaluated:
            if any(dominates(old_values, values) for _, old_values in front):
                continue

            front = [(old_solution, old_values)
                     for old_solution, old_values in front
                     if not dominates(values, old_values)]

            front.append((solution, values))

        return front