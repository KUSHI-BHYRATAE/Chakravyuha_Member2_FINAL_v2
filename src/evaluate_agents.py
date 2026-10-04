"""
evaluate_agents.py

Evaluation framework for the Chakravyuha AI Simulator.

Compares:
1. Random Agent
2. Rule-Based Agent
3. Proposed Smart Intelligent Agent

Across:
- Information levels: LOW, MEDIUM, HIGH
- Difficulty levels: LOW, MEDIUM, HIGH
- Scenarios: infiltration, escape

IMPORTANT:
The agents receive ONLY partial observations returned by
environment.get_observation() / environment.step().

ground_truth() is NOT used for decision-making.
"""

import csv
from statistics import mean

from environment import ChakravyuhaEnvironment
from agent import (
    random_agent,
    rule_based_agent,
    SmartChakravyuhaAgent,
)


# ============================================================
# CONFIGURATION
# ============================================================

INFORMATION_LEVELS = ["LOW", "MEDIUM", "HIGH"]
DIFFICULTY_LEVELS = ["LOW", "MEDIUM", "HIGH"]
SCENARIOS = ["infiltration", "escape"]

# Number of episodes for every configuration
EPISODES_PER_CONFIG = 20


# ============================================================
# RUN ONE EPISODE
# ============================================================

def run_episode(
    agent_type,
    scenario,
    information,
    difficulty,
):
    """
    Runs one complete episode.

    The agent receives only the partial observation produced
    by the environment.
    """

    env = ChakravyuhaEnvironment(
        scenario=scenario,
        information=information,
        difficulty=difficulty,
    )

    observation = env.reset()

    # Create Smart Agent only when required
    smart_agent = None

    if agent_type == "Smart":
        smart_agent = SmartChakravyuhaAgent()
        smart_agent.reset()

    while not observation["terminal"]:

        # ----------------------------------------------------
        # RANDOM AGENT
        # ----------------------------------------------------

        if agent_type == "Random":

            action = random_agent(observation)

        # ----------------------------------------------------
        # RULE-BASED AGENT
        # ----------------------------------------------------

        elif agent_type == "Rule-Based":

            action = rule_based_agent(observation)

        # ----------------------------------------------------
        # PROPOSED SMART AGENT
        # ----------------------------------------------------

        elif agent_type == "Smart":

            action, scores = smart_agent.choose_action(
                observation
            )

        else:

            raise ValueError(
                f"Unknown agent type: {agent_type}"
            )

        if action is None:
            break

        # Agent action changes the environment.
        # The returned value becomes the NEXT partial observation.
        observation = env.step(action)

    return {
        "agent": agent_type,
        "scenario": scenario,
        "information": information,
        "difficulty": difficulty,
        "success": observation["success"],
        "steps": observation["step"],
        "reward": observation["total_reward"],
        "scans": observation["scans"],
        "final_event": observation["last_event"],
    }


# ============================================================
# RUN EXPERIMENTS
# ============================================================

def run_experiments():

    agents = [
        "Random",
        "Rule-Based",
        "Smart",
    ]

    all_results = []

    total_configs = (
        len(agents)
        * len(SCENARIOS)
        * len(INFORMATION_LEVELS)
        * len(DIFFICULTY_LEVELS)
    )

    config_number = 0

    print("\n" + "=" * 75)
    print("CHAKRAVYUHA AI - AGENT PERFORMANCE EVALUATION")
    print("=" * 75)

    for agent_type in agents:

        for scenario in SCENARIOS:

            for information in INFORMATION_LEVELS:

                for difficulty in DIFFICULTY_LEVELS:

                    config_number += 1

                    print(
                        f"\n[{config_number}/{total_configs}] "
                        f"Agent={agent_type} | "
                        f"Scenario={scenario.upper()} | "
                        f"Information={information} | "
                        f"Difficulty={difficulty}"
                    )

                    config_results = []

                    for episode in range(
                        EPISODES_PER_CONFIG
                    ):

                        result = run_episode(
                            agent_type,
                            scenario,
                            information,
                            difficulty,
                        )

                        config_results.append(result)
                        all_results.append(result)

                    success_rate = (
                        sum(
                            1
                            for r in config_results
                            if r["success"]
                        )
                        / len(config_results)
                        * 100
                    )

                    avg_reward = mean(
                        r["reward"]
                        for r in config_results
                    )

                    avg_steps = mean(
                        r["steps"]
                        for r in config_results
                    )

                    avg_scans = mean(
                        r["scans"]
                        for r in config_results
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

    return all_results


# ============================================================
# SAVE RAW RESULTS
# ============================================================

def save_results(results):

    filename = "agent_evaluation_results.csv"

    fieldnames = [
        "agent",
        "scenario",
        "information",
        "difficulty",
        "success",
        "steps",
        "reward",
        "scans",
        "final_event",
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)

    print(
        f"\nRaw experiment results saved to: "
        f"{filename}"
    )


# ============================================================
# OVERALL AGENT COMPARISON
# ============================================================

def print_overall_summary(results):

    print("\n" + "=" * 75)
    print("OVERALL AGENT COMPARISON")
    print("=" * 75)

    header = (
        f"{'Agent':<15}"
        f"{'Success Rate':<18}"
        f"{'Avg Reward':<15}"
        f"{'Avg Steps':<15}"
        f"{'Avg Scans':<15}"
    )

    print(header)
    print("-" * 75)

    for agent_type in [
        "Random",
        "Rule-Based",
        "Smart",
    ]:

        agent_results = [
            r
            for r in results
            if r["agent"] == agent_type
        ]

        success_rate = (
            sum(
                1
                for r in agent_results
                if r["success"]
            )
            / len(agent_results)
            * 100
        )

        avg_reward = mean(
            r["reward"]
            for r in agent_results
        )

        avg_steps = mean(
            r["steps"]
            for r in agent_results
        )

        avg_scans = mean(
            r["scans"]
            for r in agent_results
        )

        print(
            f"{agent_type:<15}"
            f"{success_rate:<18.2f}"
            f"{avg_reward:<15.2f}"
            f"{avg_steps:<15.2f}"
            f"{avg_scans:<15.2f}"
        )


# ============================================================
# SUMMARY BY INFORMATION LEVEL
# ============================================================

def print_information_summary(results):

    print("\n" + "=" * 75)
    print("PERFORMANCE BY INFORMATION LEVEL")
    print("=" * 75)

    for information in INFORMATION_LEVELS:

        print(
            f"\nInformation Level: {information}"
        )

        for agent_type in [
            "Random",
            "Rule-Based",
            "Smart",
        ]:

            filtered = [
                r
                for r in results
                if r["agent"] == agent_type
                and r["information"] == information
            ]

            success_rate = (
                sum(
                    1
                    for r in filtered
                    if r["success"]
                )
                / len(filtered)
                * 100
            )

            avg_reward = mean(
                r["reward"]
                for r in filtered
            )

            print(
                f"{agent_type:<12} | "
                f"Success: {success_rate:>6.2f}% | "
                f"Reward: {avg_reward:>7.2f}"
            )


# ============================================================
# SUMMARY BY DIFFICULTY
# ============================================================

def print_difficulty_summary(results):

    print("\n" + "=" * 75)
    print("PERFORMANCE BY DIFFICULTY")
    print("=" * 75)

    for difficulty in DIFFICULTY_LEVELS:

        print(
            f"\nDifficulty: {difficulty}"
        )

        for agent_type in [
            "Random",
            "Rule-Based",
            "Smart",
        ]:

            filtered = [
                r
                for r in results
                if r["agent"] == agent_type
                and r["difficulty"] == difficulty
            ]

            success_rate = (
                sum(
                    1
                    for r in filtered
                    if r["success"]
                )
                / len(filtered)
                * 100
            )

            avg_reward = mean(
                r["reward"]
                for r in filtered
            )

            print(
                f"{agent_type:<12} | "
                f"Success: {success_rate:>6.2f}% | "
                f"Reward: {avg_reward:>7.2f}"
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    results = run_experiments()

    save_results(results)

    print_overall_summary(results)

    print_information_summary(results)

    print_difficulty_summary(results)

    print("\n" + "=" * 75)
    print("EVALUATION COMPLETED")
    print("=" * 75)
