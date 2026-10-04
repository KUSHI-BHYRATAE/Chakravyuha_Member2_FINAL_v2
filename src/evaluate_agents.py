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
    difficulty,
    episode
):

    env = ChakravyuhaEnvironment(
        scenario=scenario,
        information=information,
        difficulty=difficulty,
        seed=episode
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
        "Agent": agent_name,
        "Scenario": scenario.upper(),
        "Information": information,
        "Difficulty": difficulty,
        "Episode": episode + 1,
        "Success": int(
            observation["success"]
        ),
        "Steps": observation["step"],
        "Reward": observation["total_reward"],
        "Scans": observation["scans"],
        "Final_Event": observation["last_event"]
    }


# ============================================================
# MAIN EVALUATION
# ============================================================

if __name__ == "__main__":

    random.seed(42)

    results = []

    total_runs = (
        len(AGENTS)
        *
        len(SCENARIOS)
        *
        len(INFORMATION_LEVELS)
        *
        len(DIFFICULTY_LEVELS)
        *
        EPISODES_PER_CONFIG
    )

    print("=" * 70)
    print(
        "CHAKRAVYUHA AI — AGENT EVALUATION"
    )
    print("=" * 70)

    print(
        f"Total evaluation runs: {total_runs}\n"
    )


    for agent_name in AGENTS:

        print(
            f"\nEvaluating {agent_name} Agent..."
        )

        for scenario in SCENARIOS:

            for information in INFORMATION_LEVELS:

                for difficulty in DIFFICULTY_LEVELS:

                    for episode in range(
                        EPISODES_PER_CONFIG
                    ):

                        result = run_episode(
                            agent_name,
                            scenario,
                            information,
                            difficulty,
                            episode
                        )

                        results.append(
                            result
                        )

        print(
            f"✅ {agent_name} completed."
        )


    # ========================================================
    # DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        results
    )


    # ========================================================
    # SAVE RESULTS
    # ========================================================

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


    # ========================================================
    # SUMMARY FUNCTION
    # ========================================================

    def summarize(group_columns):

        summary = (
            df.groupby(group_columns)
            .agg(
                Success_Rate=(
                    "Success",
                    lambda x:
                    x.mean() * 100
                ),
                Avg_Reward=(
                    "Reward",
                    "mean"
                ),
                Avg_Steps=(
                    "Steps",
                    "mean"
                ),
                Avg_Scans=(
                    "Scans",
                    "mean"
                )
            )
            .reset_index()
        )

        for column in [
            "Success_Rate",
            "Avg_Reward",
            "Avg_Steps",
            "Avg_Scans"
        ]:
            summary[column] = (
                summary[column]
                .round(2)
            )

        return summary


    # ========================================================
    # OVERALL
    # ========================================================

    print(
        "\n\n===== OVERALL AGENT COMPARISON =====\n"
    )

    overall = summarize(
        ["Agent"]
    )

    print(
        overall.to_string(
            index=False
        )
    )


    # ========================================================
    # INFORMATION LEVEL
    # ========================================================

    print(
        "\n\n===== INFORMATION LEVEL COMPARISON =====\n"
    )

    info_summary = summarize(
        [
            "Agent",
            "Information"
        ]
    )

    print(
        info_summary.to_string(
            index=False
        )
    )


    # ========================================================
    # DIFFICULTY LEVEL
    # ========================================================

    print(
        "\n\n===== DIFFICULTY LEVEL COMPARISON =====\n"
    )

    difficulty_summary = summarize(
        [
            "Agent",
            "Difficulty"
        ]
    )

    print(
        difficulty_summary.to_string(
            index=False
        )
    )


    # ========================================================
    # SCENARIO
    # ========================================================

    print(
        "\n\n===== SCENARIO COMPARISON =====\n"
    )

    scenario_summary = summarize(
        [
            "Agent",
            "Scenario"
        ]
    )

    print(
        scenario_summary.to_string(
            index=False
        )
    )


    print(
        "\n✅ Evaluation complete!"
    )

    print(
        "📁 Results saved as:",
        output_file
    )
