from environment import ChakravyuhaEnvironment
from agent import SmartChakravyuhaAgent


# ============================================================
# DISPLAY PARTIAL OBSERVATION
# ============================================================

def display_grid(grid):

    for row in grid:
        print(" ".join(row))

    print()


# ============================================================
# DEMO SETTINGS
# ============================================================

SCENARIO = "infiltration"
INFORMATION = "MEDIUM"
DIFFICULTY = "HIGH"


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


# ============================================================
# DEMO HEADER
# ============================================================

print("=" * 65)

print(
    "SMART CHAKRAVYUHA AGENT — "
    "PARTIAL OBSERVATION DEMO"
)

print("=" * 65)


print(
    f"\nScenario    : "
    f"{SCENARIO.upper()}"
)

print(
    f"Information : "
    f"{INFORMATION}"
)

print(
    f"Difficulty  : "
    f"{DIFFICULTY}"
)


print(
    f"\nStart       : "
    f"{observation['agent']}"
)

print(
    f"Goal        : "
    f"{observation['goal']}"
)


print(
    "\nInitial Partial Observation:\n"
)


display_grid(
    observation["grid"]
)


# ============================================================
# RUN SMART AGENT
# ============================================================

while not observation["terminal"]:

    previous_position = (
        observation["agent"]
    )


    action, scores = (
        agent.choose_action(
            observation
        )
    )


    if action is None:

        print(
            "No valid action available."
        )

        break


    print("-" * 65)

    print(
        f"STEP "
        f"{observation['step'] + 1}"
    )

    print(
        f"Current Position : "
        f"{previous_position}"
    )

    print(
        f"Uncertainty      : "
        f"{observation['uncertainty']}%"
    )

    print(
        f"Chosen Action    : "
        f"{action}"
    )


    if action == "SCAN":

        print(
            "Decision Reason   : "
            "Gathering information "
            "under uncertainty"
        )

    elif action in {
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT"
    }:

        print(
            "Decision Reason   : "
            "A* goal-directed "
            "risk-aware movement"
        )

    else:

        print(
            "Decision Reason   : "
            "Utility-based fallback"
        )


    observation = env.step(
        action
    )


    print(
        f"New Position     : "
        f"{observation['agent']}"
    )

    print(
        f"Environment Event: "
        f"{observation['last_event']}"
    )

    print(
        f"Current Reward   : "
        f"{observation['total_reward']}"
    )

    print(
        f"Scans Used       : "
        f"{observation['scans']}"
    )


    print(
        "\nAgent's Partial View:\n"
    )


    display_grid(
        observation["grid"]
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 65)
print("FINAL RESULT")
print("=" * 65)


print(
    f"Success      : "
    f"{observation['success']}"
)

print(
    f"Final Event  : "
    f"{observation['last_event']}"
)

print(
    f"Total Steps  : "
    f"{observation['step']}"
)

print(
    f"Total Reward : "
    f"{observation['total_reward']}"
)

print(
    f"Total Scans  : "
    f"{observation['scans']}"
)


if observation["success"]:

    print(
        "\n✅ SMART AGENT "
        "SUCCESSFULLY REACHED THE GOAL"
    )

else:

    print(
        "\n❌ SMART AGENT "
        "DID NOT REACH THE GOAL"
    )


print("=" * 65)
