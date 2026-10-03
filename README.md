# Chakravyuha — Member 2 FINAL

## Run
Open a terminal in this exact folder and run:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Member 2 module
This version contains:
- environment state
- three scenarios
- low/medium/high information access
- low/medium/high difficulty
- partial observability
- hidden and visible threats
- SCAN information expansion
- valid-action validation
- rewards
- terminal success/failure
- research ground truth
- manual mode
- working baseline AI mode

## Member 1 integration
Use this interface:

```python
observation = env.get_observation()
action = agent.choose_action(observation)
next_observation = env.step(action)
```

Do not expose `true_world()` or `ground_truth()` to the decision agent.
