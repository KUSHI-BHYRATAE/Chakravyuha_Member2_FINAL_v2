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

## Last run (30 episodes x 27 settings x 5 agents = 4050 episodes)
| Agent | Success % | Defeat % | Timeout % | Avg reward | Avg steps | Avg scans |
|---|---|---|---|---|---|---|
| Random | 0.7 | 74.9 | 24.3 | -9.88 | 18.7 | 4.14 |
| Old app baseline (before the AI agent was connected) | 0.0 | 0.0 | 100.0 | -24.35 | 45 | 45 |
| Greedy (rule-based) | 77.7 | 0.0 | 22.3 | 22.96 | 25.7 | 0 |
| Cautious planner | 100.0 | 0.0 | 0.0 | 28.19 | 17.9 | 0 |
| Smart AI agent (Member 1) | 70.4 | 0.0 | 29.6 | 18.79 | 26.2 | 10.56 |

The Smart AI agent never gets defeated, but it times out in 8 of 27 settings:
infiltration and reconnaissance at HIGH difficulty (all information levels),
and escape at MEDIUM difficulty with LOW or MEDIUM information.

## Issues found during testing
- FIXED: the old `baseline_action` in app.py scanned forever and never moved.
  app.py now uses Member 1's Smart AI agent instead.
- "reconnaissance" behaves exactly like "infiltration" in environment.py.
- `seed` is unused and enemies never move, so the environment is deterministic.
- Adjacent cells are always visible, so information level barely matters.
