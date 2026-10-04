import random
import heapq


# ============================================================
# RANDOM BASELINE
# ============================================================

def random_agent(observation):
    valid = observation["valid_actions"]

    if not valid:
        return None

    return random.choice(valid)


# ============================================================
# RULE-BASED BASELINE
# ============================================================

def rule_based_agent(observation):
    valid = observation["valid_actions"]

    if not valid:
        return None

    r, c = observation["agent"]
    gr, gc = observation["goal"]

    # Simple uncertainty rule
    if observation["uncertainty"] > 70 and "SCAN" in valid:
        return "SCAN"

    preferred = []

    if r > gr:
        preferred.append("UP")

    if r < gr:
        preferred.append("DOWN")

    if c > gc:
        preferred.append("LEFT")

    if c < gc:
        preferred.append("RIGHT")

    for action in preferred:
        if action in valid:
            return action

    for action in ["UP", "DOWN", "LEFT", "RIGHT"]:
        if action in valid:
            return action

    if "WAIT" in valid:
        return "WAIT"

    return valid[0]


# ============================================================
# PROPOSED INTELLIGENT AGENT
# ============================================================

class SmartChakravyuhaAgent:

    MOVES = {
        "UP": (-1, 0),
        "DOWN": (1, 0),
        "LEFT": (0, -1),
        "RIGHT": (0, 1)
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.known_map = {}
        self.visited = {}
        self.scanned_positions = set()
        self.last_position = None
        self.last_action = None

    # ========================================================
    # BASIC HELPERS
    # ========================================================

    def _distance(self, a, b):
        return (
            abs(a[0] - b[0])
            +
            abs(a[1] - b[1])
        )

    def _update_memory(self, observation):
        grid = observation["grid"]

        for r in range(len(grid)):
            for c in range(len(grid[r])):

                cell = grid[r][c]

                if cell != "?":
                    self.known_map[(r, c)] = cell

    # ========================================================
    # INFORMATION GAIN
    # ========================================================

    def _information_gain(self, observation):

        grid = observation["grid"]
        current = tuple(observation["agent"])

        r, c = current
        radius = 2
        gain = 0

        for nr in range(len(grid)):
            for nc in range(len(grid[0])):

                if (
                    abs(nr - r) + abs(nc - c) <= radius
                    and grid[nr][nc] == "?"
                ):
                    gain += 1

        return gain

    # ========================================================
    # THREAT RISK
    # ========================================================

    def _enemy_risk(self, position):

        risk = 0

        for pos, cell in self.known_map.items():

            if cell != "E":
                continue

            d = self._distance(position, pos)

            if d == 0:
                return 1000

            elif d == 1:
                risk += 25

            elif d == 2:
                risk += 6

        return risk

    # ========================================================
    # A* PLANNING
    # ========================================================

    def _astar(self, start, goal, observation):

        rows = len(observation["grid"])
        cols = len(observation["grid"][0])

        valid_actions = observation["valid_actions"]

        queue = []
        counter = 0

        heapq.heappush(
            queue,
            (0, counter, start)
        )

        came_from = {
            start: None
        }

        action_from = {}

        g_score = {
            start: 0
        }

        while queue:

            _, _, current = heapq.heappop(queue)

            if current == goal:
                break

            for action, (dr, dc) in self.MOVES.items():

                nr = current[0] + dr
                nc = current[1] + dc

                if not (
                    0 <= nr < rows
                    and 0 <= nc < cols
                ):
                    continue

                # First action must be currently valid
                if (
                    current == start
                    and action not in valid_actions
                ):
                    continue

                new_pos = (nr, nc)

                cell = self.known_map.get(
                    new_pos,
                    "?"
                )

                # Never intentionally enter known danger
                if cell in ("X", "E"):
                    continue

                # Cost model
                if cell == "G":
                    move_cost = 0.5

                elif cell in (".", "P"):
                    move_cost = 1.0

                else:
                    # Unknown cells carry uncertainty cost
                    move_cost = 1.6

                # Small revisit penalty
                move_cost += (
                    0.35
                    *
                    self.visited.get(
                        new_pos,
                        0
                    )
                )

                # Known threat risk
                move_cost += self._enemy_risk(
                    new_pos
                )

                new_g = (
                    g_score[current]
                    +
                    move_cost
                )

                if (
                    new_pos not in g_score
                    or new_g < g_score[new_pos]
                ):

                    g_score[new_pos] = new_g
                    came_from[new_pos] = current
                    action_from[new_pos] = action

                    heuristic = self._distance(
                        new_pos,
                        goal
                    )

                    counter += 1

                    heapq.heappush(
                        queue,
                        (
                            new_g + heuristic,
                            counter,
                            new_pos
                        )
                    )

        if goal not in came_from:
            return []

        path = []
        current = goal

        while current != start:

            path.append(
                action_from[current]
            )

            current = came_from[current]

        path.reverse()

        return path

    # ========================================================
    # SCAN UTILITY
    # ========================================================

    def _should_scan(self, observation, path):

        current = tuple(
            observation["agent"]
        )

        if "SCAN" not in observation["valid_actions"]:
            return False

        # Do not scan same position repeatedly
        if current in self.scanned_positions:
            return False

        uncertainty = observation["uncertainty"]

        gain = self._information_gain(
            observation
        )

        scans_used = observation["scans"]

        # Dynamic scan budget
        if uncertainty >= 80:
            max_scans = 3

        elif uncertainty >= 55:
            max_scans = 2

        else:
            max_scans = 1

        if scans_used >= max_scans:
            return False

        # Information-gathering utility
        scan_utility = (
            gain * 1.5
            +
            uncertainty * 0.05
            -
            scans_used * 4
        )

        # Scan after discovering a blocked route
        if (
            observation["last_event"] == "blocked_move"
            and gain >= 2
        ):
            return True

        # High uncertainty + useful local information
        if (
            uncertainty > 70
            and gain >= 3
            and scan_utility > 8
        ):
            return True

        # Long uncertain route
        if (
            len(path) >= 6
            and uncertainty > 50
            and gain >= 4
            and scan_utility > 9
        ):
            return True

        return False

    # ========================================================
    # UTILITY-BASED FALLBACK
    # ========================================================

    def _fallback(self, observation):

        current = tuple(
            observation["agent"]
        )

        goal = tuple(
            observation["goal"]
        )

        valid = observation[
            "valid_actions"
        ]

        grid = observation["grid"]

        scores = {}

        current_distance = self._distance(
            current,
            goal
        )

        for action, (dr, dc) in self.MOVES.items():

            if action not in valid:
                continue

            new_pos = (
                current[0] + dr,
                current[1] + dc
            )

            cell = grid[
                new_pos[0]
            ][
                new_pos[1]
            ]

            if cell in ("X", "E"):
                continue

            new_distance = self._distance(
                new_pos,
                goal
            )

            score = 0

            # Goal progress
            score += (
                current_distance
                -
                new_distance
            ) * 8

            # Goal itself
            if cell == "G":
                score += 100

            # Exploration value
            if cell == "?":
                score += 2

            # Revisit cost
            score -= (
                self.visited.get(
                    new_pos,
                    0
                )
                * 5
            )

            # Threat cost
            score -= self._enemy_risk(
                new_pos
            )

            scores[action] = score

        if not scores:
            return None, {}

        best = max(
            scores,
            key=scores.get
        )

        return best, scores

    # ========================================================
    # MAIN DECISION ENGINE
    # ========================================================

    def choose_action(self, observation):

        valid = observation[
            "valid_actions"
        ]

        if not valid:
            return None, {}

        current = tuple(
            observation["agent"]
        )

        goal = tuple(
            observation["goal"]
        )

        # Update belief/memory map
        self._update_memory(
            observation
        )

        self.visited[current] = (
            self.visited.get(
                current,
                0
            )
            +
            1
        )

        # ----------------------------------------------------
        # GOAL IMMEDIATELY REACHABLE
        # ----------------------------------------------------

        if self._distance(current, goal) == 1:

            for action, (dr, dc) in self.MOVES.items():

                if action not in valid:
                    continue

                new_pos = (
                    current[0] + dr,
                    current[1] + dc
                )

                if new_pos == goal:

                    self.last_position = current
                    self.last_action = action

                    return (
                        action,
                        {
                            action: 1000
                        }
                    )

        # ----------------------------------------------------
        # GENERATE A* PLAN
        # ----------------------------------------------------

        path = self._astar(
            current,
            goal,
            observation
        )

        # ----------------------------------------------------
        # INFORMATION-GATHERING DECISION
        # ----------------------------------------------------

        if self._should_scan(
            observation,
            path
        ):

            self.scanned_positions.add(
                current
            )

            self.last_action = "SCAN"

            return (
                "SCAN",
                {
                    "SCAN":
                    self._information_gain(
                        observation
                    )
                }
            )

        # ----------------------------------------------------
        # FOLLOW A* PLAN
        # ----------------------------------------------------

        if path:

            action = path[0]

            if action in valid:

                self.last_position = current
                self.last_action = action

                return (
                    action,
                    {
                        action: 100
                    }
                )

        # ----------------------------------------------------
        # UTILITY FALLBACK
        # ----------------------------------------------------

        action, scores = self._fallback(
            observation
        )

        if action is not None:

            self.last_position = current
            self.last_action = action

            return (
                action,
                scores
            )

        # ----------------------------------------------------
        # INFORMATION FALLBACK
        # ----------------------------------------------------

        if (
            "SCAN" in valid
            and current not in self.scanned_positions
        ):

            self.scanned_positions.add(
                current
            )

            return (
                "SCAN",
                {
                    "SCAN": 1
                }
            )

        # ----------------------------------------------------
        # LAST RESORT
        # ----------------------------------------------------

        if "WAIT" in valid:

            return (
                "WAIT",
                {
                    "WAIT": -100
                }
            )

        return None, {}


print(
    "✅ FINAL SmartChakravyuhaAgent V3 loaded!"
)
