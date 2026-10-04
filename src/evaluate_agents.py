import random
import os
import pandas as pd

from environment import ChakravyuhaEnvironment
from agent import (
    random_agent,
    rule_based_agent,
    SmartChakravyuhaAgent
)


# ============================================================
# SETTINGS
# ============================================================

AGENTS = [
    "Random",
    "Rule-Based",
    "Smart"
]

SCENARIOS = [
    "infiltration",
    "escape"
]

INFORMATION_LEVELS = [
    "LOW",
    "MEDIUM",
    "HIGH"
]

DIFFICULTY_LEVELS = [
    "LOW",
    "MEDIUM",
    "HIGH"
]

EPISODES_PER_CONFIG = 20


# ============================================================
# RUN ONE EPISODE
# ============================================================

def run_episode(
    agent_name,
    scenario,
    information,
    difficulty
):

    env = ChakravyuhaEnvironment(
        scenario=scenario,
        information=information,
        difficulty=difficulty
    )

    observation = env.reset()

    if agent_name == "Smart":
        agent = SmartChakravyuhaAgent()
        agent.reset()
    else:
        agent = None


    while not observation["terminal"]:

        if agent_name == "Random":

            action = random_agent(
                observation
            )

        elif agent_name == "Rule-Based":

            action = rule_based_agent(
                observation
            )

        elif agent_name == "Smart":

            action, scores = agent.choose_action(
                observation
            )

        else:

            raise ValueError(
                "Unknown agent type"
            )


        if action is None:
            break


        observation = env.step(
            action
        )


    return {

        "agent":
            agent_name,

        "scenario":
            scenario,

        "information":
            information,

        "difficulty":
            difficulty,

        "success":
            observation["success"],

        "steps":
            observation["step"],

        "reward":
            observation["total_reward"],

        "scans":
            observation["scans"],

        "final_event":
            observation["last_event"]
    }


# ============================================================
# RUN EXPERIMENTS
# ============================================================

results = []


total_configs = (

    len(AGENTS)
    *
    len(SCENARIOS)
    *
    len(INFORMATION_LEVELS)
    *
    len(DIFFICULTY_LEVELS)
)


config_number = 0


print("=" * 75)
print("CHAKRAVYUHA AI AGENT EVALUATION")
print("=" * 75)


for agent_name in AGENTS:

    for scenario in SCENARIOS:

        for information in INFORMATION_LEVELS:

            for difficulty in DIFFICULTY_LEVELS:

                config_number += 1

                config_results = []


                for episode in range(
                    EPISODES_PER_CONFIG
                ):

                    result = run_episode(
                        agent_name,
                        scenario,
                        information,
                        difficulty
                    )

                    results.append(
                        result
                    )

                    config_results.append(
                        result
                    )


                success_rate = (

                    sum(
                        r["success"]
                        for r in config_results
                    )

                    /
                    EPISODES_PER_CONFIG

                    *
                    100
                )


                avg_reward = (

                    sum(
                        r["reward"]
                        for r in config_results
                    )

                    /
                    EPISODES_PER_CONFIG
                )


                avg_steps = (

                    sum(
                        r["steps"]
                        for r in config_results
                    )

                    /
                    EPISODES_PER_CONFIG
                )


                avg_scans = (

                    sum(
                        r["scans"]
                        for r in config_results
                    )

                    /
                    EPISODES_PER_CONFIG
                )


                print(
                    f"\n[{config_number}/{total_configs}] "
                    f"Agent={agent_name} | "
                    f"Scenario={scenario.upper()} | "
                    f"Information={information} | "
                    f"Difficulty={difficulty}"
                )


                print(
                    f"Success Rate : "
                    f"{success_rate:.1f}%"
                )

                print(
                    f"Average Reward: "
                    f"{avg_reward:.2f}"
                )

                print(
                    f"Average Steps : "
                    f"{avg_steps:.2f}"
                )

                print(
                    f"Average Scans : "
                    f"{avg_scans:.2f}"
                )


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(
    results
)


# ============================================================
# SAVE RESULTS
# ============================================================

os.makedirs(
    "results",
    exist_ok=True
)


output_file = os.path.join(
    "results",
    "agent_evaluation_results.csv"
)


df.to_csv(
    output_file,
    index=False
)


print(
    "\nRaw experiment results saved to:",
    output_file
)


# ============================================================
# OVERALL COMPARISON
# ============================================================

print("\n")
print("=" * 75)
print("OVERALL AGENT COMPARISON")
print("=" * 75)


print(
    f"{'Agent':<15}"
    f"{'Success Rate':<18}"
    f"{'Avg Reward':<15}"
    f"{'Avg Steps':<15}"
    f"{'Avg Scans':<15}"
)


print("-" * 75)


for agent_name in AGENTS:

    agent_df = df[
        df["agent"]
        ==
        agent_name
    ]


    success_rate = (
        agent_df["success"].mean()
        *
        100
    )

    avg_reward = (
        agent_df["reward"].mean()
    )

    avg_steps = (
        agent_df["steps"].mean()
    )

    avg_scans = (
        agent_df["scans"].mean()
    )


    print(
        f"{agent_name:<15}"
        f"{success_rate:<18.2f}"
        f"{avg_reward:<15.2f}"
        f"{avg_steps:<15.2f}"
        f"{avg_scans:<15.2f}"
    )


# ============================================================
# INFORMATION LEVEL RESULTS
# ============================================================

print("\n")
print("=" * 75)
print("PERFORMANCE BY INFORMATION LEVEL")
print("=" * 75)


for information in INFORMATION_LEVELS:

    print(
        f"\nInformation Level: "
        f"{information}"
    )


    subset = df[
        df["information"]
        ==
        information
    ]


    for agent_name in AGENTS:

        agent_df = subset[
            subset["agent"]
            ==
            agent_name
        ]


        success_rate = (
            agent_df["success"].mean()
            *
            100
        )


        avg_reward = (
            agent_df["reward"].mean()
        )


        print(
            f"{agent_name:<12} | "
            f"Success: "
            f"{success_rate:6.2f}% | "
            f"Reward: "
            f"{avg_reward:7.2f}"
        )


# ============================================================
# DIFFICULTY RESULTS
# ============================================================

print("\n")
print("=" * 75)
print("PERFORMANCE BY DIFFICULTY")
print("=" * 75)


for difficulty in DIFFICULTY_LEVELS:

    print(
        f"\nDifficulty: "
        f"{difficulty}"
    )


    subset = df[
        df["difficulty"]
        ==
        difficulty
    ]


    for agent_name in AGENTS:

        agent_df = subset[
            subset["agent"]
            ==
            agent_name
        ]


        success_rate = (
            agent_df["success"].mean()
            *
            100
        )


        avg_reward = (
            agent_df["reward"].mean()
        )


        print(
            f"{agent_name:<12} | "
            f"Success: "
            f"{success_rate:6.2f}% | "
            f"Reward: "
            f"{avg_reward:7.2f}"
        )


print("\n")
print("=" * 75)
print("EVALUATION COMPLETED")
print("=" * 75)
