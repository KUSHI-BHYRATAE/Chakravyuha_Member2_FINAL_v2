"""Metric calculations for the evaluation module (Person 4)."""
from __future__ import annotations

from statistics import mean, pstdev


def episode_record(env, agent_name, config, episode, invalid_actions):
    """One row describing how a single episode ended."""
    s = env.state
    obs = env.get_observation()
    return {
        "agent": agent_name,
        "scenario": config["scenario"],
        "information": config["information"],
        "difficulty": config["difficulty"],
        "episode": episode,
        "success": int(s.success),
        "defeated": int(s.last_event == "agent_defeated"),
        "timed_out": int(s.last_event == "step_limit_reached"),
        "steps": s.step,
        "total_reward": round(s.total_reward, 2),
        "scans": s.scans,
        "invalid_actions": invalid_actions,
        "final_uncertainty": obs["uncertainty"],
    }


def summarise(rows):
    """Aggregate a list of episode rows into the headline metrics."""
    n = len(rows)
    wins = [r for r in rows if r["success"]]
    return {
        "episodes": n,
        "success_rate": round(100 * len(wins) / n, 1),
        "defeat_rate": round(100 * sum(r["defeated"] for r in rows) / n, 1),
        "timeout_rate": round(100 * sum(r["timed_out"] for r in rows) / n, 1),
        "avg_reward": round(mean(r["total_reward"] for r in rows), 2),
        "std_reward": round(pstdev(r["total_reward"] for r in rows), 2),
        "avg_steps": round(mean(r["steps"] for r in rows), 1),
        "avg_steps_when_success": round(mean(r["steps"] for r in wins), 1) if wins else None,
        "avg_scans": round(mean(r["scans"] for r in rows), 2),
        "avg_invalid_actions": round(mean(r["invalid_actions"] for r in rows), 2),
        "avg_final_uncertainty": round(mean(r["final_uncertainty"] for r in rows), 1),
    }


def group_summary(rows, keys):
    """Summarise rows grouped by the given column names."""
    groups = {}
    for r in rows:
        groups.setdefault(tuple(r[k] for k in keys), []).append(r)
    out = []
    for key, items in groups.items():
        row = dict(zip(keys, key))
        row.update(summarise(items))
        out.append(row)
    return out
