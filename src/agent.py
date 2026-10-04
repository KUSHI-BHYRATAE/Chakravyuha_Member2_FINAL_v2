
import random
import heapq


# ============================================================
# 1. RANDOM BASELINE AGENT
# ============================================================

def random_agent(observation):
    """
    Select a random action from the currently valid actions.
    """

    valid_actions = observation["valid_actions"]

    if not valid_actions:
        return None

    return random.choice(valid_actions)


# ============================================================
# 2. RULE-BASED BASELINE AGENT
# ============================================================

def rule_based_agent(observation):
    """
    Simple baseline agent.

    Uses only partial observations.
    """

    valid = observation["valid_actions"]

    if not valid:
        return None

    uncertainty = observation["uncertainty"]

    x, y = observation["agent"]
    gx, gy = observation["goal"]

    if uncertainty > 70 and "SCAN" in valid:
        return "SCAN"

    if x > gx and "UP" in valid:
        return "UP"

    if x < gx and "DOWN" in valid:
        return "DOWN"

    if y > gy and "LEFT" in valid:
        return "LEFT"

    if y < gy and "RIGHT" in valid:
        return "RIGHT"

    if "SCAN" in valid:
        return "SCAN"

    if "WAIT" in valid:
        return "WAIT"

    return valid[0]


# ============================================================
# 3. PROPOSED SMART A* AGENT
# ============================================================

class SmartChakravyuhaAgent:
    """
    Intelligent agent for the partially observable
    Chakravyuha environment.

    Features:
    - Partial-observation decision making
    - Internal belief-map memory
    - A* path planning
    - Goal-directed movement
    - Known threat avoidance
    - Risk-aware exploration
    - Uncertainty-aware scanning
    - Revisit/loop avoidance
    - Utility-based fallback

    The agent never accesses ground_truth() or true_world().
    """

    def __init__(self):
        self.reset()


    # ========================================================
    # RESET MEMORY
    # ========================================================

    def reset(self):

        self.visited = {}

        self.scanned_positions = set()

        self.known_map = {}

        self.last_position = None

        self.last_action = None

        self.best_distance = float("inf")

        self.no_progress_count = 0


    # ========================================================
    # MANHATTAN DISTANCE
    # ========================================================

    def _distance(self, a, b):

        return (
            abs(a[0] - b[0])
            +
            abs(a[1] - b[1])
        )


    # ========================================================
    # UPDATE BELIEF MAP
    # ========================================================

    def _update_memory(self, observation):

        grid = observation["grid"]

        for r in range(len(grid)):

            for c in range(len(grid[r])):

                cell = grid[r][c]

                if cell != "?":

                    self.known_map[(r, c)] = cell


    # ========================================================
    # COUNT UNKNOWN CELLS
    # ========================================================

    def _unknown_nearby(
        self,
        position,
        grid,
        radius=1
    ):

        r, c = position

        count = 0

        for dr in range(-radius, radius + 1):

            for dc in range(-radius, radius + 1):

                if dr == 0 and dc == 0:
                    continue

                nr = r + dr
                nc = c + dc

                if (
                    0 <= nr < len(grid)
                    and
                    0 <= nc < len(grid[0])
                ):

                    if grid[nr][nc] == "?":
                        count += 1

        return count


    # ========================================================
    # KNOWN ENEMY RISK
    # ========================================================

    def _enemy_risk(self, position):

        risk = 0

        for enemy_position, cell in self.known_map.items():

            if cell != "E":
                continue

            distance = self._distance(
                position,
                enemy_position
            )

            if distance == 0:
                return 1000

            elif distance == 1:
                risk += 20

            elif distance == 2:
                risk += 6

        return risk


    # ========================================================
    # GET A* NEIGHBOURS
    # ========================================================

    def _get_neighbours(
        self,
        position,
        grid,
        start,
        valid_actions
    ):

        r, c = position

        directions = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1)
        }

        neighbours = []

        rows = len(grid)
        cols = len(grid[0])

        for action, (dr, dc) in directions.items():

            nr = r + dr
            nc = c + dc

            if not (
                0 <= nr < rows
                and
                0 <= nc < cols
            ):
                continue

            # At the real current position, use only
            # observation-safe valid actions.
            if (
                position == start
                and
                action not in valid_actions
            ):
                continue

            next_position = (nr, nc)

            cell = self.known_map.get(
                next_position,
                "?"
            )

            # Known obstacle or known enemy
            if cell in ("X", "E"):
                continue

            # --------------------------------------------
            # BASE MOVEMENT COST
            # --------------------------------------------

            if cell == "G":

                cost = 0.5

            elif cell in (".", "P"):

                cost = 1.0

            else:

                # Unknown cells are traversable,
                # but slightly risky.
                cost = 2.2

            # --------------------------------------------
            # REVISIT PENALTY
            # --------------------------------------------

            visits = self.visited.get(
                next_position,
                0
            )

            cost += visits * 2.5

            # --------------------------------------------
            # THREAT RISK
            # --------------------------------------------

            cost += self._enemy_risk(
                next_position
            )

            neighbours.append(
                (
                    next_position,
                    action,
                    cost
                )
            )

        return neighbours


    # ========================================================
    # A* PATH PLANNING
    # ========================================================

    def _astar(
        self,
        start,
        goal,
        grid,
        valid_actions
    ):

        frontier = []

        counter = 0

        heapq.heappush(
            frontier,
            (
                0,
                counter,
                start
            )
        )

        came_from = {
            start: None
        }

        action_from = {}

        cost_so_far = {
            start: 0
        }

        while frontier:

            _, _, current = heapq.heappop(
                frontier
            )

            if current == goal:
                break

            neighbours = self._get_neighbours(
                current,
                grid,
                start,
                valid_actions
            )

            for (
                next_position,
                action,
                move_cost
            ) in neighbours:

                new_cost = (
                    cost_so_far[current]
                    +
                    move_cost
                )

                if (
                    next_position not in cost_so_far
                    or
                    new_cost
                    <
                    cost_so_far[next_position]
                ):

                    cost_so_far[next_position] = (
                        new_cost
                    )

                    # A*: f(n) = g(n) + h(n)
                    priority = (
                        new_cost
                        +
                        self._distance(
                            next_position,
                            goal
                        )
                    )

                    counter += 1

                    heapq.heappush(
                        frontier,
                        (
                            priority,
                            counter,
                            next_position
                        )
                    )

                    came_from[next_position] = (
                        current
                    )

                    action_from[next_position] = (
                        action
                    )

        # No route found
        if goal not in came_from:
            return []

        # --------------------------------------------
        # RECONSTRUCT PATH
        # --------------------------------------------

        path = []

        current = goal

        while current != start:

            action = action_from[current]

            path.append(action)

            current = came_from[current]

        path.reverse()

        return path


    # ========================================================
    # UTILITY-BASED FALLBACK
    # ========================================================

    def _fallback_action(self, observation):

        valid = observation["valid_actions"]

        current = tuple(
            observation["agent"]
        )

        goal = tuple(
            observation["goal"]
        )

        grid = observation["grid"]

        directions = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1)
        }

        current_distance = self._distance(
            current,
            goal
        )

        scores = {}

        for action in valid:

            # ============================================
            # MOVEMENT
            # ============================================

            if action in directions:

                dr, dc = directions[action]

                nr = current[0] + dr
                nc = current[1] + dc

                next_position = (
                    nr,
                    nc
                )

                cell = grid[nr][nc]

                if cell == "E":

                    scores[action] = -1000
                    continue

                score = 0

                new_distance = self._distance(
                    next_position,
                    goal
                )

                # Goal progress
                if new_distance < current_distance:
                    score += 10

                elif new_distance == current_distance:
                    score += 2

                else:
                    score -= 3

                # Cell knowledge
                if cell == "G":
                    score += 100

                elif cell == "?":
                    score += 4

                elif cell == ".":
                    score += 1

                # Revisit penalty
                visits = self.visited.get(
                    next_position,
                    0
                )

                score -= visits * 7

                # Enemy risk
                score -= self._enemy_risk(
                    next_position
                )

                # Encourage exploration when stuck
                if (
                    self.no_progress_count >= 3
                    and
                    visits == 0
                ):
                    score += 8

                # Avoid immediate backtracking
                if (
                    self.last_position is not None
                    and
                    next_position == self.last_position
                ):
                    score -= 6

                scores[action] = score

            # ============================================
            # SCAN
            # ============================================

            elif action == "SCAN":

                unknown = self._unknown_nearby(
                    current,
                    grid,
                    radius=1
                )

                if current in self.scanned_positions:

                    scores[action] = -25

                elif unknown == 0:

                    scores[action] = -15

                else:

                    scores[action] = 6

            # ============================================
            # WAIT
            # ============================================

            elif action == "WAIT":

                scores[action] = -30

        if not scores:
            return None, {}

        best_action = max(
            scores,
            key=scores.get
        )

        return best_action, scores


    # ========================================================
    # MAIN DECISION ENGINE
    # ========================================================

    def choose_action(self, observation):

        valid = observation["valid_actions"]

        if not valid:
            return None, {}

        current = tuple(
            observation["agent"]
        )

        goal = tuple(
            observation["goal"]
        )

        grid = observation["grid"]

        uncertainty = observation["uncertainty"]

        # --------------------------------------------
        # 1. Update belief map
        # --------------------------------------------

        self._update_memory(
            observation
        )

        # --------------------------------------------
        # 2. Record visit
        # --------------------------------------------

        self.visited[current] = (
            self.visited.get(current, 0)
            +
            1
        )

        # --------------------------------------------
        # 3. Monitor progress
        # --------------------------------------------

        current_distance = self._distance(
            current,
            goal
        )

        if current_distance < self.best_distance:

            self.best_distance = current_distance

            self.no_progress_count = 0

        else:

            self.no_progress_count += 1

        # --------------------------------------------
        # 4. Uncertainty-aware scan
        # --------------------------------------------

        unknown_count = self._unknown_nearby(
            current,
            grid,
            radius=1
        )

        should_scan = (
            "SCAN" in valid
            and
            current not in self.scanned_positions
            and
            unknown_count >= 2
            and
            current_distance > 1
            and
            (
                uncertainty > 60
                or
                self.no_progress_count >= 4
            )
        )

        if should_scan:

            self.scanned_positions.add(
                current
            )

            self.last_action = "SCAN"

            return (
                "SCAN",
                {
                    "SCAN": 10
                }
            )

        # --------------------------------------------
        # 5. A* path planning
        # --------------------------------------------

        path = self._astar(
            start=current,
            goal=goal,
            grid=grid,
            valid_actions=valid
        )

        if path:

            planned_action = path[0]

            if planned_action in valid:

                self.last_position = current

                self.last_action = (
                    planned_action
                )

                return (
                    planned_action,
                    {
                        planned_action: 20
                    }
                )

        # --------------------------------------------
        # 6. Utility fallback
        # --------------------------------------------

        action, scores = self._fallback_action(
            observation
        )

        if action == "SCAN":

            self.scanned_positions.add(
                current
            )

        self.last_position = current

        self.last_action = action

        return action, scores
