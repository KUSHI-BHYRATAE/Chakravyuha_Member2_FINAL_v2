"""Experiment runner for the evaluation module (Person 4).

Runs every agent on every scenario / information / difficulty setting,
saves raw + summary CSVs and the graphs for the PPT.

    python -m evaluation.experiments                 # 30 episodes per setting
    python -m evaluation.experiments --episodes 100
"""
from __future__ import annotations

import argparse
import csv
import itertools
import os

from src.environment import ChakravyuhaEnvironment
from evaluation.baseline_agents import default_agents
from evaluation.metrics import episode_record, summarise, group_summary

SCENARIOS = ["infiltration", "reconnaissance", "escape"]
INFORMATION = ["LOW", "MEDIUM", "HIGH"]
DIFFICULTY = ["LOW", "MEDIUM", "HIGH"]


def run_episode(env, agent):
    """Play one episode. Returns the number of invalid actions the agent tried."""
    obs = env.reset()
    agent.reset()
    invalid = 0
    # invalid actions do not advance env.step, so cap the loop separately
    for _ in range(env.MAX_STEPS * 4):
        if obs["terminal"]:
            break
        choose = getattr(agent, "choose_action", None) or agent.act
        action = choose(obs)
        if isinstance(action, tuple):  # agent may return (action, scores)
            action = action[0]
        obs = env.step(action)
        if obs["last_event"] == "invalid_action":
            invalid += 1
    return invalid


def run_all(episodes=30, seed=42):
    rows = []
    agents = default_agents(seed)
    for scenario, info, diff in itertools.product(SCENARIOS, INFORMATION, DIFFICULTY):
        config = {"scenario": scenario, "information": info, "difficulty": diff}
        for agent in agents:
            env = ChakravyuhaEnvironment(**config)
            for ep in range(episodes):
                invalid = run_episode(env, agent)
                rows.append(episode_record(env, agent.name, config, ep, invalid))
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_plots(rows, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    agents = list(dict.fromkeys(r["agent"] for r in rows))
    overall = {a: summarise([r for r in rows if r["agent"] == a]) for a in agents}

    def bar(metric, ylabel, title, fname):
        fig, ax = plt.subplots(figsize=(6, 4))
        vals = [overall[a][metric] for a in agents]
        bars = ax.bar(agents, vals, color=["#9aa0a6", "#4c78a8", "#e8a33d", "#2e7d6b", "#7b4ea3"][: len(agents)])
        ax.bar_label(bars, fmt="%.1f")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, fname), dpi=200)
        plt.close(fig)

    bar("success_rate", "Success rate (%)", "Success rate by agent", "success_rate.png")
    bar("avg_reward", "Average total reward", "Average reward by agent", "avg_reward.png")
    bar("avg_steps", "Average steps per episode", "Steps taken by agent", "avg_steps.png")

    def grouped(key, levels, title, fname):
        fig, ax = plt.subplots(figsize=(7, 4))
        width = 0.8 / len(agents)
        for i, a in enumerate(agents):
            vals = [
                summarise([r for r in rows if r["agent"] == a and r[key] == lv])["success_rate"]
                for lv in levels
            ]
            ax.bar([j + i * width for j in range(len(levels))], vals, width, label=a)
        ax.set_xticks([j + width * (len(agents) - 1) / 2 for j in range(len(levels))])
        ax.set_xticklabels(levels)
        ax.set_xlabel(key.capitalize() + " level")
        ax.set_ylabel("Success rate (%)")
        ax.set_ylim(0, 125)
        ax.set_title(title)
        ax.legend(fontsize=8, loc="upper center", ncol=len(agents))
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, fname), dpi=200)
        plt.close(fig)

    grouped("information", INFORMATION, "Success rate vs information access", "success_vs_information.png")
    grouped("difficulty", DIFFICULTY, "Success rate vs difficulty", "success_vs_difficulty.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="evaluation/results")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rows = run_all(args.episodes, args.seed)

    write_csv(os.path.join(args.out, "episodes.csv"), rows)
    by_agent = group_summary(rows, ["agent"])
    write_csv(os.path.join(args.out, "summary_by_agent.csv"), by_agent)
    write_csv(
        os.path.join(args.out, "summary_by_setting.csv"),
        group_summary(rows, ["agent", "scenario", "information", "difficulty"]),
    )
    make_plots(rows, args.out)

    print(f"\n{len(rows)} episodes run. Results saved in '{args.out}/'\n")
    print(f"{'Agent':<28}{'Success%':>9}{'Defeat%':>9}{'Timeout%':>10}{'AvgReward':>11}{'AvgSteps':>10}{'AvgScans':>10}")
    for r in by_agent:
        print(f"{r['agent']:<28}{r['success_rate']:>9}{r['defeat_rate']:>9}{r['timeout_rate']:>10}"
              f"{r['avg_reward']:>11}{r['avg_steps']:>10}{r['avg_scans']:>10}")


if __name__ == "__main__":
    main()
