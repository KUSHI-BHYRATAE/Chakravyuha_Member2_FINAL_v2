"""Baseline agents for the evaluation module (Person 4).

Every agent follows one interface so the evaluator can treat them the same:

    agent.reset()                 -> called at the start of each episode
    agent.act(observation) -> str -> one of the env's action names

Agents only see the observation dict from environment.get_observation().
They never touch ground truth.
"""
from __future__ import annotations

import heapq
import random

MOVES = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}


class RandomAgent:
    """Lower bound: picks any valid action uniformly at random."""

    name = "Random"

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def reset(self):
        pass

    def act(self, obs):
        return self.rng.choice(obs["valid_actions"])


class AppBaselineAgent:
    """The rule app.py used in "AI Agent" mode before Member 1's agent was
    connected (the old baseline_action): scan while uncertainty is above 55%, otherwise
    step straight toward the goal."""

    name = "Old app baseline"

    def __init__(self, seed=None):
        pass

    def reset(self):
        pass

    def act(self, o):
        valid = o["valid_actions"]
        if "SCAN" in valid and o["uncertainty"] > 55:
            return "SCAN"
        x, y = o["agent"]
        gx, gy = o["goal"]
        if x > gx and "UP" in valid: return "UP"
        if x < gx and "DOWN" in valid: return "DOWN"
        if y > gy and "LEFT" in valid: return "LEFT"
        if y < gy and "RIGHT" in valid: return "RIGHT"
        return "WAIT" if "WAIT" in valid else valid[0]


class GreedyAgent:
    """Rule-based: always step toward the goal, never scans.

    Avoids enemies it can already see, but walks blindly into unknown cells.
    Shows what happens when an agent ignores uncertainty.
    """

    name = "Greedy (rule-based)"

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.visits = {}

    def reset(self):
        self.visits = {}

    def act(self, obs):
        x, y = obs["agent"]
        gx, gy = obs["goal"]
        grid = obs["grid"]
        self.visits[(x, y)] = self.visits.get((x, y), 0) + 1

        options = []
        for a in obs["valid_actions"]:
            if a not in MOVES:
                continue
            nx, ny = x + MOVES[a][0], y + MOVES[a][1]
            if grid[nx][ny] == "E":
                continue
            dist = abs(nx - gx) + abs(ny - gy)
            # prefer closer cells, break loops by penalising revisits
            score = dist + 2 * self.visits.get((nx, ny), 0)
            options.append((score, self.rng.random(), a))
        if not options:
            return "WAIT"
        return min(options)[2]


class CautiousPlannerAgent:
    """Uncertainty-aware baseline: plans a path on the *known* map and
    scans before stepping into a cell it has not seen yet.

    Dijkstra over the observed grid: known-free cells cost 1, unknown cells
    cost more (risk), known obstacles/enemies are blocked.
    """

    name = "Cautious planner"

    def __init__(self, seed=None, unknown_cost=3.0):
        self.unknown_cost = unknown_cost
        self.blocked = set()

    def reset(self):
        self.blocked = set()

    def _plan(self, obs):
        grid = obs["grid"]
        n = len(grid)
        start, goal = tuple(obs["agent"]), tuple(obs["goal"])
        dist = {start: 0.0}
        first = {start: None}
        heap = [(0.0, start)]
        while heap:
            d, cur = heapq.heappop(heap)
            if cur == goal:
                return first[cur]
            if d > dist[cur]:
                continue
            for a, (dx, dy) in MOVES.items():
                nxt = (cur[0] + dx, cur[1] + dy)
                if not (0 <= nxt[0] < n and 0 <= nxt[1] < n):
                    continue
                cell = grid[nxt[0]][nxt[1]]
                if cell in ("X", "E") or nxt in self.blocked:
                    continue
                nd = d + (self.unknown_cost if cell == "?" else 1.0)
                if nd < dist.get(nxt, float("inf")):
                    dist[nxt] = nd
                    first[nxt] = a if cur == start else first[cur]
                    heapq.heappush(heap, (nd, nxt))
        return None

    def act(self, obs):
        x, y = obs["agent"]
        grid = obs["grid"]
        valid = obs["valid_actions"]

        for _ in range(4):
            action = self._plan(obs)
            if action is None:
                return "SCAN" if obs["last_event"] != "scan_no_new_information" else "WAIT"
            target = (x + MOVES[action][0], y + MOVES[action][1])
            if action not in valid:
                # env refuses the move -> there is an unseen obstacle there
                self.blocked.add(target)
                continue
            unseen = grid[target[0]][target[1]] == "?"
            if unseen and obs["last_event"] not in (
                "scan_revealed_information", "scan_no_new_information"
            ):
                return "SCAN"
            return action
        return "WAIT"


def default_agents(seed=None):
    """Agents compared in the experiments. Add the team's AI agent here."""
    agents = [RandomAgent(seed), AppBaselineAgent(seed), GreedyAgent(seed),
              CautiousPlannerAgent(seed)]
    # Member 1's AI agent (src/agent.py)
    try:
        from src.agent import SmartChakravyuhaAgent
        smart = SmartChakravyuhaAgent()
        smart.name = "Smart AI agent"
        agents.append(smart)
    except ImportError:
        pass  # agent file not in the repo yet -> baselines only
    return agents
