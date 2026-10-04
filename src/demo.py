from environment import ChakravyuhaEnvironment
from agent import SmartChakravyuhaAgent


# ============================================================
# SETTINGS
# ============================================================

SCENARIO = "infiltration"
INFORMATION = "MEDIUM"
DIFFICULTY = "HIGH"


# ============================================================
# DISPLAY OBSERVATION
# ============================================================

def display_grid(observation):

    print()

    for row in observation["grid"]:
        print(" ".join(row))

    print()


# ============================================================
# CREATE ENVIRONMENT + AGENT
# ============================================================

env = ChakravyuhaEnvironment(
    scenario=SCENARIO,
    information=INFORMATION,
    difficulty=DIFFICULTY
)

agent = SmartChakravyuhaAgent()

observation = env.reset()
agent.reset()


print("=" * 70)
print("CHAKRAVYUHA AI — SMART AGENT DEMO")
print("=" * 70)

print("Scenario    :", SCENARIO.upper())
print("Information :", INFORMATION)
print("Difficulty  :", DIFFICULTY)

print("\nLegend:")
print("P = Agent")
print("G = Goal")
print("X = Known Obstacle")
print("E = Known Enemy")
print("? = Unknown Cell")
print(". = Revealed Safe Cell")

print("\nINITIAL OBSERVATION")

display_grid(
    observation
)


# ============================================================
# RUN SMART AGENT
# ============================================================

while not observation["terminal"]:

    old_position = observation["agent"]

    action, scores = agent.choose_action(
        observation
    )


    if action is None:
        print("No valid action available.")
        break


    # --------------------------------------------------------
    # EXPLAIN DECISION
    # --------------------------------------------------------

    if action == "SCAN":

        reason = (
            "Uncertainty-aware information gathering"
        )

    elif action in [
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT"
    ]:

        reason = (
            "A* goal-directed / risk-aware planning"
        )

    else:

        reason = (
            "Fallback action"
        )


    observation = env.step(
        action
    )


    print("-" * 70)

    print(
        f"Step {observation['step']}"
    )

    print(
        "Position:",
        old_position,
        "->",
        observation["agent"]
    )

    print(
        "Selected Action:",
        action
    )

    print(
        "Decision Reason:",
        reason
    )

    print(
        "Environment Event:",
        observation["last_event"]
    )

    print(
        "Uncertainty:",
        f"{observation['uncertainty']:.2f}%"
    )

    print(
        "Total Reward:",
        round(
            observation["total_reward"],
            2
        )
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("FINAL RESULT")
print("=" * 70)

print(
    "Success      :",
    observation["success"]
)

print(
    "Final Event  :",
    observation["last_event"]
)

print(
    "Final Position:",
    observation["agent"]
)

print(
    "Goal         :",
    observation["goal"]
)

print(
    "Steps        :",
    observation["step"]
)

print(
    "Scans        :",
    observation["scans"]
)

print(
    "Total Reward :",
    round(
        observation["total_reward"],
        2
    )
)

print("=" * 70)
