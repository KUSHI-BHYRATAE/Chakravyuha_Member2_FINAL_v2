from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set

Position = Tuple[int, int]


@dataclass
class EnvironmentState:
    agent: Position
    goal: Position
    enemies: Set[Position] = field(default_factory=set)
    obstacles: Set[Position] = field(default_factory=set)
    step: int = 0
    total_reward: float = 0.0
    scans: int = 0
    terminal: bool = False
    success: bool = False
    last_event: str = "episode_started"


class ChakravyuhaEnvironment:
    """Member 2 simulation environment: ground truth + partial observation."""

    SIZE = 9
    MAX_STEPS = 45
    ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT", "SCAN", "WAIT"]

    def __init__(self, scenario="infiltration", information="MEDIUM",
                 difficulty="MEDIUM", seed=None):
        self.scenario = scenario.lower()
        self.information = information.upper()
        self.difficulty = difficulty.upper()
        self.reset()

    def reset(self):
        center = (4, 4)
        if self.scenario == "escape":
            agent, goal = center, (8, 4)
        else:
            agent, goal = (8, 4), center

        obstacles = self._build_obstacles()
        enemies = self._build_enemies(obstacles, agent, goal)

        self.state = EnvironmentState(
            agent=agent, goal=goal,
            enemies=enemies, obstacles=obstacles
        )
        self._revealed = set()
        self._known_enemies = set()
        self._known_obstacles = set()
        self._reveal_radius(self.state.agent, self._initial_radius())
        self._rebuild_true_grid()
        return self.get_observation()

    def _build_obstacles(self):
        obstacles = {
            (1,1),(1,2),(1,6),(1,7),(2,1),(2,7),
            (3,3),(3,5),(4,2),(4,6),(5,3),(5,5),
            (6,1),(6,7),(7,1),(7,2),(7,6),(7,7)
        }
        if self.difficulty == "LOW":
            obstacles -= {(1,1),(1,7),(7,1),(7,7)}
        elif self.difficulty == "HIGH":
            obstacles |= {(2,2),(2,6),(6,2),(6,6)}
        return obstacles

    def _build_enemies(self, obstacles, agent, goal):
        candidates = [
            (7,5),(7,3),(6,4),(5,7),(5,1),
            (3,7),(3,1),(2,4),(4,7),(4,1)
        ]
        count = {"LOW": 2, "MEDIUM": 3, "HIGH": 4}[self.difficulty]
        valid = [p for p in candidates if p not in obstacles and p not in {agent, goal}]
        return set(valid[:count])

    def _initial_radius(self):
        return {"LOW": 2, "MEDIUM": 1, "HIGH": 1}[self.information]

    def _visibility_radius(self):
        return {"LOW": 1, "MEDIUM": 1, "HIGH": 2}[self.information]

    def _reveal_radius(self, center, radius):
        cx, cy = center
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                if abs(x-cx) + abs(y-cy) <= radius:
                    self._revealed.add((x,y))
        self._known_enemies = self.state.enemies & self._revealed
        self._known_obstacles = self.state.obstacles & self._revealed

    def _uncertainty(self):
        return round(100 * (1 - len(self._revealed)/(self.SIZE*self.SIZE)), 1)

    def get_observation(self):
        grid = []
        for x in range(self.SIZE):
            row = []
            for y in range(self.SIZE):
                p = (x,y)
                if p == self.state.agent:
                    v = "P"
                elif p == self.state.goal and p in self._revealed:
                    v = "G"
                elif p in self._known_enemies:
                    v = "E"
                elif p in self._known_obstacles:
                    v = "X"
                elif p in self._revealed:
                    v = "."
                else:
                    v = "?"
                row.append(v)
            grid.append(row)

        return {
            "grid": grid,
            "agent": self.state.agent,
            "goal": self.state.goal,
            "step": self.state.step,
            "total_reward": round(self.state.total_reward, 2),
            "visible_threats": len(self._known_enemies),
            "hidden_threats": len(self.state.enemies - self._known_enemies),
            "uncertainty": self._uncertainty(),
            "scans": self.state.scans,
            "last_event": self.state.last_event,
            "terminal": self.state.terminal,
            "success": self.state.success,
            "valid_actions": self.valid_actions(),
        }

    def _valid_position(self, p):
        x, y = p
        return 0 <= x < self.SIZE and 0 <= y < self.SIZE and p not in self.state.obstacles

    def valid_actions(self):
        if self.state.terminal:
            return []
        x, y = self.state.agent
        candidates = {
            "UP": (x-1,y),
            "DOWN": (x+1,y),
            "LEFT": (x,y-1),
            "RIGHT": (x,y+1),
        }
        valid = [a for a in self.ACTIONS if a in {"SCAN","WAIT"}]
        for action, pos in candidates.items():
            if self._valid_position(pos):
                valid.insert(0, action)
        order = self.ACTIONS
        return [a for a in order if a in valid]

    def step(self, action):
        action = action.upper()
        if self.state.terminal:
            return self.get_observation()

        if action not in self.valid_actions():
            self.state.total_reward -= 2
            self.state.last_event = "invalid_action"
            return self.get_observation()

        self.state.step += 1
        reward = -0.15

        if action in {"UP","DOWN","LEFT","RIGHT"}:
            reward += self._move(action)
        elif action == "SCAN":
            reward += self._scan()
        else:
            self.state.last_event = "waited"
            reward -= 0.15

        if self.state.agent == self.state.goal:
            reward += 25
            self.state.terminal = True
            self.state.success = True
            self.state.last_event = "core_breached"
        elif self.state.agent in self.state.enemies:
            reward -= 12
            self.state.terminal = True
            self.state.last_event = "agent_defeated"
        elif self.state.step >= self.MAX_STEPS:
            self.state.terminal = True
            self.state.last_event = "step_limit_reached"

        self.state.total_reward += reward
        self._rebuild_true_grid()
        return self.get_observation()

    def _move(self, action):
        dxdy = {
            "UP":(-1,0), "DOWN":(1,0),
            "LEFT":(0,-1), "RIGHT":(0,1)
        }[action]
        x,y = self.state.agent
        new = (x+dxdy[0], y+dxdy[1])
        if not self._valid_position(new):
            self.state.last_event = "blocked_move"
            return -1

        old_distance = abs(x-self.state.goal[0]) + abs(y-self.state.goal[1])
        self.state.agent = new
        self._reveal_radius(new, self._visibility_radius())
        new_distance = abs(new[0]-self.state.goal[0]) + abs(new[1]-self.state.goal[1])
        self.state.last_event = "moved"
        return 0.6 if new_distance < old_distance else -0.1

    def _scan(self):
        before = len(self._revealed)
        radius = 2 if self.information in {"LOW","MEDIUM"} else 1
        self._reveal_radius(self.state.agent, radius)
        self.state.scans += 1
        if len(self._revealed) > before:
            self.state.last_event = "scan_revealed_information"
            return 0.8
        self.state.last_event = "scan_no_new_information"
        return -0.4

    def _rebuild_true_grid(self):
        self._true_grid = [["." for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        for x,y in self.state.obstacles:
            self._true_grid[x][y] = "X"
        for x,y in self.state.enemies:
            self._true_grid[x][y] = "E"
        gx,gy = self.state.goal
        self._true_grid[gx][gy] = "G"
        ax,ay = self.state.agent
        self._true_grid[ax][ay] = "P"

    def true_world(self):
        self._rebuild_true_grid()
        return [row[:] for row in self._true_grid]

    def ground_truth(self):
        return {
            "enemies": sorted(self.state.enemies),
            "obstacles": sorted(self.state.obstacles),
            "agent": self.state.agent,
            "goal": self.state.goal,
            "step": self.state.step,
        }
