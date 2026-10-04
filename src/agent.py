
import random


# ============================================================
# 1. RANDOM BASELINE AGENT
# ============================================================

def random_agent(observation):
    """
    Selects a random action from the currently valid actions.
    Used as a baseline for evaluation.
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
    Simple rule-based agent.

    Behaviour:
    - Scans when uncertainty is high.
    - Otherwise moves toward the goal.
    - Uses only the partial observation provided by
      the environment.
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
# 3. SMART HEURISTIC / UTILITY-BASED AI AGENT
# ============================================================

class SmartChakravyuhaAgent:
    """
    Decision-making agent for partially observable environments.

    The agent considers:
    - Goal progress
    - Visible threats
    - Unknown cells
    - Information uncertainty
    - Previously visited locations
    - Previously scanned locations

    It does NOT access the hidden ground-truth environment.
    """

    def __init__(self):

        # Number of times each position has been visited
        self.visited = {}

        # Positions where SCAN has already been performed
        self.scanned_positions = set()


    def reset(self):
        """
        Clears agent memory before starting a new episode.
        """

        self.visited = {}
        self.scanned_positions = set()


    def choose_action(self, observation):

        valid = observation["valid_actions"]

        if not valid:
            return None, {}

        x, y = observation["agent"]
        gx, gy = observation["goal"]

        grid = observation["grid"]
        uncertainty = observation["uncertainty"]

        current = (x, y)

        # Record visit
        self.visited[current] = self.visited.get(current, 0) + 1

        movement = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1)
        }

        current_distance = abs(x - gx) + abs(y - gy)

        scores = {}

        # ----------------------------------------------------
        # SCORE EACH VALID ACTION
        # ----------------------------------------------------

        for action in valid:

            score = 0

            # =================================================
            # MOVEMENT ACTIONS
            # =================================================

            if action in movement:

                dx, dy = movement[action]

                new_x = x + dx
                new_y = y + dy

                new_position = (new_x, new_y)

                target_cell = grid[new_x][new_y]

                new_distance = (
                    abs(new_x - gx)
                    + abs(new_y - gy)
                )

                # ---------------------------------------------
                # Visible enemy avoidance
                # ---------------------------------------------

                if target_cell == "E":

                    score = -100

                else:

                    # -----------------------------------------
                    # Goal progress
                    # -----------------------------------------

                    if new_distance < current_distance:
                        score += 6

                    elif new_distance == current_distance:
                        score += 2

                    else:
                        score -= 1


                    # -----------------------------------------
                    # Cell information
                    # -----------------------------------------

                    if target_cell == ".":
                        score += 2

                    elif target_cell == "?":
                        score -= 1

                    elif target_cell == "G":
                        score += 30


                    # -----------------------------------------
                    # Loop avoidance
                    # -----------------------------------------

                    visits = self.visited.get(
                        new_position,
                        0
                    )

                    score -= visits * 4


            # =================================================
            # SCAN ACTION
            # =================================================

            elif action == "SCAN":

                # Avoid scanning the same position repeatedly
                if current in self.scanned_positions:

                    score = -10

                elif uncertainty > 70:

                    score = 7

                elif uncertainty > 40:

                    score = 3

                else:

                    score = -2


            # =================================================
            # WAIT ACTION
            # =================================================

            elif action == "WAIT":

                score = -10


            scores[action] = score


        # ----------------------------------------------------
        # SELECT HIGHEST-SCORING ACTION
        # ----------------------------------------------------

        best_action = max(
            scores,
            key=scores.get
        )


        # Remember scanned locations
        if best_action == "SCAN":

            self.scanned_positions.add(current)


        return best_action, scores
