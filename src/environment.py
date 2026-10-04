from dataclasses import dataclass


@dataclass
class EnvironmentState:
    agent: tuple
    goal: tuple
    enemies: set
    obstacles: set
    step: int = 0
    total_reward: float = 0.0
    scans: int = 0
    terminal: bool = False
    success: bool = False
    last_event: str = "start"


class ChakravyuhaEnvironment:

    SIZE = 9
    MAX_STEPS = 45

    MOVEMENTS = {
        "UP": (-1, 0),
        "DOWN": (1, 0),
        "LEFT": (0, -1),
        "RIGHT": (0, 1)
    }

    ACTIONS = [
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT",
        "SCAN",
        "WAIT"
    ]


    def __init__(
        self,
        scenario="infiltration",
        information="MEDIUM",
        difficulty="MEDIUM",
        seed=None
    ):

        self.scenario = scenario.lower()
        self.information = information.upper()
        self.difficulty = difficulty.upper()
        self.seed = seed

        self.known_obstacles = set()
        self.known_enemies = set()
        self.revealed = set()

        self.reset()


    # ========================================================
    # RESET ENVIRONMENT
    # ========================================================

    def reset(self):

        self.known_obstacles = set()
        self.known_enemies = set()
        self.revealed = set()

        if self.scenario == "escape":
            agent = (4, 4)
            goal = (8, 4)

        else:
            agent = (8, 4)
            goal = (4, 4)


        # ----------------------------------------------------
        # DIFFICULTY-BASED OBSTACLE LAYOUT
        # ----------------------------------------------------

        if self.difficulty == "LOW":

            obstacles = {
                (6, 2),
                (6, 6),
                (2, 2),
                (2, 6)
            }

        elif self.difficulty == "HIGH":

            obstacles = {
                (6, 2),
                (6, 3),
                (6, 4),
                (6, 5),

                (5, 2),
                (5, 6),

                (4, 3),
                (4, 5),

                (2, 2),
                (2, 3),
                (2, 5),
                (2, 6),

                (3, 6),
                (7, 2)
            }

        else:

            obstacles = {
                (6, 3),
                (6, 4),
                (6, 5),

                (2, 2),
                (2, 3),
                (2, 5),
                (2, 6),

                (4, 1),
                (4, 7)
            }


        # Start and goal must remain accessible
        obstacles.discard(agent)
        obstacles.discard(goal)


        # ----------------------------------------------------
        # DIFFICULTY-BASED ENEMIES
        # ----------------------------------------------------

        enemy_candidates = [
            (5, 1),
            (3, 7),
            (1, 1),
            (1, 7)
        ]

        if self.difficulty == "LOW":
            enemy_count = 1

        elif self.difficulty == "HIGH":
            enemy_count = 4

        else:
            enemy_count = 2


        enemies = set(
            enemy_candidates[:enemy_count]
        )

        enemies.discard(agent)
        enemies.discard(goal)

        enemies = enemies - obstacles


        self.state = EnvironmentState(
            agent=agent,
            goal=goal,
            enemies=enemies,
            obstacles=obstacles
        )


        # ----------------------------------------------------
        # INITIAL INFORMATION
        # ----------------------------------------------------

        if self.information == "LOW":
            radius = 0

        elif self.information == "HIGH":
            radius = 2

        else:
            radius = 1


        self._reveal_radius(
            agent,
            radius
        )


        return self.get_observation()


    # ========================================================
    # REVEAL LOCAL AREA
    # ========================================================

    def _reveal_radius(
        self,
        center,
        radius
    ):

        cr, cc = center

        for r in range(self.SIZE):

            for c in range(self.SIZE):

                if (
                    abs(r - cr)
                    +
                    abs(c - cc)
                    <= radius
                ):

                    pos = (r, c)

                    self.revealed.add(pos)

                    if pos in self.state.obstacles:
                        self.known_obstacles.add(pos)

                    if pos in self.state.enemies:
                        self.known_enemies.add(pos)


    # ========================================================
    # UNCERTAINTY
    # ========================================================

    def _uncertainty(self):

        total_cells = (
            self.SIZE
            *
            self.SIZE
        )

        unknown_cells = (
            total_cells
            -
            len(self.revealed)
        )

        return (
            unknown_cells
            /
            total_cells
            *
            100
        )


    # ========================================================
    # VALID ACTIONS
    # ========================================================

    def valid_actions(self):

        valid = [
            "SCAN",
            "WAIT"
        ]

        r, c = self.state.agent

        for action, (dr, dc) in (
            self.MOVEMENTS.items()
        ):

            nr = r + dr
            nc = c + dc

            new_pos = (
                nr,
                nc
            )


            if not (
                0 <= nr < self.SIZE
                and
                0 <= nc < self.SIZE
            ):
                continue


            # Only KNOWN obstacles are excluded.
            # Hidden obstacles remain uncertain.
            if (
                new_pos
                in self.known_obstacles
            ):
                continue


            valid.append(action)


        return valid


    # ========================================================
    # OBSERVATION
    # ========================================================

    def get_observation(self):

        grid = [
            ["?" for _ in range(self.SIZE)]
            for _ in range(self.SIZE)
        ]


        for r, c in self.revealed:

            if (
                (r, c)
                in self.known_obstacles
            ):
                grid[r][c] = "X"

            elif (
                (r, c)
                in self.known_enemies
            ):
                grid[r][c] = "E"

            else:
                grid[r][c] = "."


        gr, gc = self.state.goal
        grid[gr][gc] = "G"

        ar, ac = self.state.agent
        grid[ar][ac] = "P"


        return {

            "grid":
                grid,

            "agent":
                self.state.agent,

            "goal":
                self.state.goal,

            "uncertainty":
                self._uncertainty(),

            "valid_actions":
                self.valid_actions(),

            "step":
                self.state.step,

            "total_reward":
                self.state.total_reward,

            "scans":
                self.state.scans,

            "terminal":
                self.state.terminal,

            "success":
                self.state.success,

            "last_event":
                self.state.last_event
        }


    # ========================================================
    # STEP
    # ========================================================

    def step(self, action):

        if self.state.terminal:
            return self.get_observation()


        reward = 0.0


        if action not in self.valid_actions():

            reward = -2.0
            self.state.last_event = "invalid_action"


        elif action in self.MOVEMENTS:

            reward = self._move(
                action
            )


        elif action == "SCAN":

            reward = self._scan()


        elif action == "WAIT":

            reward = -0.5
            self.state.last_event = "wait"


        self.state.step += 1

        self.state.total_reward += reward


        # ----------------------------------------------------
        # GOAL
        # ----------------------------------------------------

        if (
            self.state.agent
            ==
            self.state.goal
        ):

            self.state.total_reward += 25.0

            self.state.success = True
            self.state.terminal = True
            self.state.last_event = (
                "goal_reached"
            )


        # ----------------------------------------------------
        # STEP LIMIT
        # ----------------------------------------------------

        elif (
            self.state.step
            >=
            self.MAX_STEPS
        ):

            self.state.terminal = True
            self.state.success = False
            self.state.last_event = (
                "step_limit"
            )


        return self.get_observation()


    # ========================================================
    # MOVEMENT
    # ========================================================

    def _move(self, action):

        dr, dc = self.MOVEMENTS[action]

        old_pos = self.state.agent

        new_pos = (
            old_pos[0] + dr,
            old_pos[1] + dc
        )


        # ----------------------------------------------------
        # HIDDEN OBSTACLE ENCOUNTER
        # ----------------------------------------------------

        if (
            new_pos
            in self.state.obstacles
        ):

            self.revealed.add(
                new_pos
            )

            self.known_obstacles.add(
                new_pos
            )

            self.state.last_event = (
                "blocked_move"
            )

            return -1.0


        # ----------------------------------------------------
        # SUCCESSFUL MOVEMENT
        # ----------------------------------------------------

        old_distance = (
            abs(old_pos[0] - self.state.goal[0])
            +
            abs(old_pos[1] - self.state.goal[1])
        )


        new_distance = (
            abs(new_pos[0] - self.state.goal[0])
            +
            abs(new_pos[1] - self.state.goal[1])
        )


        self.state.agent = new_pos


        # Movement reveals immediate neighbourhood
        self._reveal_radius(
            new_pos,
            1
        )


        # ----------------------------------------------------
        # ENEMY ENCOUNTER
        # ----------------------------------------------------

        if (
            new_pos
            in self.state.enemies
        ):

            self.known_enemies.add(
                new_pos
            )

            self.state.last_event = (
                "enemy_encounter"
            )

            return -5.0


        # ----------------------------------------------------
        # PROGRESS REWARD
        # ----------------------------------------------------

        if new_distance < old_distance:

            reward = 0.6

        else:

            reward = -0.1


        self.state.last_event = "moved"

        return reward


    # ========================================================
    # SCAN
    # ========================================================

    def _scan(self):

        before = len(
            self.revealed
        )


        if self.information == "LOW":
            radius = 1

        elif self.information == "HIGH":
            radius = 3

        else:
            radius = 2


        self._reveal_radius(
            self.state.agent,
            radius
        )


        after = len(
            self.revealed
        )


        self.state.scans += 1


        if after > before:

            self.state.last_event = (
                "scan_revealed_information"
            )

            return 0.8


        self.state.last_event = (
            "scan_no_new_information"
        )

        return -0.4


    # ========================================================
    # DEBUG / EVALUATION ONLY
    # ========================================================

    def true_world(self):

        return {
            "agent":
                self.state.agent,

            "goal":
                self.state.goal,

            "obstacles":
                set(
                    self.state.obstacles
                ),

            "enemies":
                set(
                    self.state.enemies
                )
        }


    def ground_truth(self):

        return self.true_world()


print(
    "✅ REDESIGNED environment.py loaded successfully!"
)
