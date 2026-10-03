# Evaluation module (Member 4)

Runs every agent on every scenario / information / difficulty setting and
saves metrics + graphs.

```
pip install -r requirements.txt
python -m evaluation.experiments              # run from the repo root
python -m evaluation.experiments --episodes 100
```
Output goes to `evaluation/results/` (3 CSVs, 5 graphs).

To add the team's AI agent, append it in `baseline_agents.py -> default_agents()`.
It needs `.name`, `.reset()` and `.choose_action(obs)`.

## Last run (30 episodes x 27 settings x 4 agents = 3240 episodes)
| Agent | Success % | Defeat % | Timeout % | Avg reward | Avg steps |
|---|---|---|---|---|---|
| Random | 0.7 | 74.9 | 24.3 | -9.88 | 18.7 |
| App baseline (current AI mode in app.py) | 0.0 | 0.0 | 100.0 | -24.35 | 45 |
| Greedy (rule-based) | 77.7 | 0.0 | 22.3 | 22.96 | 25.7 |
| Cautious planner | 100.0 | 0.0 | 0.0 | 28.19 | 17.9 |

## Issues found during testing
- `baseline_action` in app.py scans forever: uncertainty never drops below 55%
  by scanning in place, so it never moves and always times out.
- "reconnaissance" behaves exactly like "infiltration" in environment.py.
- `seed` is unused and enemies never move, so the environment is deterministic.
- Adjacent cells are always visible, so information level barely matters.
