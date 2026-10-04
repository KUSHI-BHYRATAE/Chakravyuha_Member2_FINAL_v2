# Evaluation module (Member 4)

Runs every agent on every scenario / information / difficulty setting and
saves metrics + graphs.

```
pip install -r requirements.txt
python -m evaluation.experiments              # run from the repo root
python -m evaluation.experiments --episodes 100
```
Output goes to `evaluation/results/` (3 CSVs, 5 graphs).

Member 1's agent (`src/agent.py`, `SmartChakravyuhaAgent`) is picked up
automatically when that file is in the repo. Without it, only baselines run.

## Last run (30 episodes x 27 settings x 4 agents = 3240 episodes)
Run on the redesigned environment (enemies now cost -5 reward instead of
ending the episode; information levels reveal radius 0 / 1 / 2).

| Agent | Success % | Timeout % | Avg reward | Avg steps | Avg scans | Enemy hits |
|---|---|---|---|---|---|---|
| Random | 8.4 | 91.6 | 1.94 | 43.7 | 8.7 | 0.39 |
| Greedy (rule-based) | 87.7 | 12.3 | 27.29 | 16.7 | 0 | 0 |
| Cautious planner | 100.0 | 0.0 | 29.83 | 13.0 | 0.33 | 0 |
| Smart AI agent (proposed, A*) | 100.0 | 0.0 | 31.03 | 17.2 | 1.33 | 0 |

The proposed agent and the cautious planner both always succeed. The proposed
agent earns the highest reward; the planner needs the fewest steps.

## Known limitations
- "reconnaissance" still behaves exactly like "infiltration".
- `seed` is still unused and enemies do not move, so the environment is
  deterministic: deterministic agents give the same result every episode.
- Episodes can no longer end in defeat, so "defeat rate" is always 0 and enemy
  encounters are reported instead.
