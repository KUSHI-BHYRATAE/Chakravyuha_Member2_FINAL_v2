import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.environment import ChakravyuhaEnvironment

def test_initial_state():
    env = ChakravyuhaEnvironment()
    obs = env.get_observation()
    assert len(obs["grid"]) == 9
    assert len(obs["grid"][0]) == 9
    assert obs["step"] == 0
    assert "SCAN" in obs["valid_actions"]

def test_partial_observation():
    env = ChakravyuhaEnvironment("infiltration", "MEDIUM", "MEDIUM")
    flat = [v for row in env.get_observation()["grid"] for v in row]
    assert "?" in flat

def test_scan():
    env = ChakravyuhaEnvironment()
    before = env.get_observation()["uncertainty"]
    env.step("SCAN")
    after = env.get_observation()["uncertainty"]
    assert after <= before
    assert env.state.scans == 1

def test_ground_truth():
    env = ChakravyuhaEnvironment()
    truth = env.ground_truth()
    assert truth["agent"] == env.state.agent
    assert truth["goal"] == env.state.goal
