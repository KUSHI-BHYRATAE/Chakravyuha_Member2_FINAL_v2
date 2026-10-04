from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st
import csv

from src.environment import ChakravyuhaEnvironment
from src.agent import SmartChakravyuhaAgent

st.set_page_config(
    page_title="Chakravyuha Strategic AI Lab",
    page_icon="⚔️",
    layout="wide",
)

# ---------- Hero image ----------
ASSET = Path(__file__).parent / "assets" / "mahabharata_chariot.png"
B64 = base64.b64encode(ASSET.read_bytes()).decode("utf-8")
HERO = f"data:image/png;base64,{B64}"

# ---------- CSS ----------
st.markdown(
f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');

.stApp {{
    background: #eee7da;
}}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg,#0b1322 0%,#17243a 100%);
    border-right: 1px solid #26344b;
}}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {{
    color: #fff8ea !important;
}}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
    color: #f7ead5 !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    letter-spacing: 1.1px !important;
}}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
    color: #c9d0dc !important;
    font-size: 14px !important;
}}

/* Select boxes: WHITE box + DARK, clearly readable value */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background: #ffffff !important;
    border: 1px solid #d9d1c5 !important;
    border-radius: 12px !important;
    min-height: 50px !important;
}}
[data-testid="stSidebar"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] div[data-baseweb="select"] input,
[data-testid="stSidebar"] div[data-baseweb="select"] div[role="button"] {{
    color: #182235 !important;
    font-weight: 700 !important;
    font-size: 15px !important;
}}
[data-testid="stSidebar"] div[data-baseweb="select"] svg {{
    fill: #182235 !important;
    color: #182235 !important;
}}
/* Dropdown menu itself */
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li {{
    background: #ffffff !important;
    color: #182235 !important;
}}
div[data-baseweb="popover"] li * {{
    color: #182235 !important;
}}

/* Sidebar reset buttons: dark readable text */
[data-testid="stSidebar"] .stButton button {{
    background: #ffffff !important;
    color: #182235 !important;
    border: 1px solid #d8d0c4 !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    font-weight: 800 !important;
}}
[data-testid="stSidebar"] .stButton button p,
[data-testid="stSidebar"] .stButton button span {{
    color: #182235 !important;
}}

/* ---------- Hero ---------- */
.hero {{
    background-image: linear-gradient(90deg,rgba(4,8,15,.93),rgba(4,8,15,.45)),url("{HERO}");
    background-size: cover;
    background-position: center;
    border-radius: 0 0 30px 30px;
    padding: 54px 58px;
    margin: -1rem -1rem 28px -1rem;
    min-height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 18px 50px rgba(0,0,0,.20);
}}
.eyebrow {{
    color:#e3b34c;
    font-size:13px;
    font-weight:800;
    letter-spacing:4px;
    margin-bottom:14px;
}}
.hero-title {{
    color:#fff8ea;
    font-family:Cinzel,serif;
    font-size:58px;
    font-weight:700;
    line-height:1;
    margin-bottom:20px;
}}
.hero-sub {{
    color:#f3e8d6;
    font-size:16px;
    max-width:900px;
    line-height:1.7;
    font-weight:500;
}}

/* ---------- Metric cards ---------- */
.metric-card {{
    background:rgba(255,255,255,.97);
    border:1px solid #d7cdbd;
    border-radius:18px;
    padding:17px 18px;
    min-height:100px;
    box-shadow:0 5px 18px rgba(0,0,0,.05);
}}
.metric-label {{
    color:#6f6b64;
    font-size:11px;
    font-weight:800;
    letter-spacing:1.5px;
}}
.metric-value {{
    color:#172033;
    font-size:26px;
    font-weight:800;
    margin-top:9px;
}}

.panel {{
    background:rgba(255,255,255,.96);
    border:1px solid #d7cdbd;
    border-radius:18px;
    padding:22px;
    color:#202638;
}}
.section-title {{
    color:#202638;
    font-family:Cinzel,serif;
    font-size:24px;
    font-weight:700;
}}
.world {{
    display:grid;
    grid-template-columns:repeat(9,minmax(30px,1fr));
    gap:6px;
    background:#121b2a;
    padding:13px;
    border-radius:19px;
}}
.cell {{
    aspect-ratio:1;
    display:flex;
    align-items:center;
    justify-content:center;
    border-radius:8px;
    font-weight:800;
    font-size:14px;
}}
.u {{background:#26364e;color:#9aabc0;}}
.e {{background:#eee8dc;color:#8d8478;}}
.p {{background:#2563eb;color:#fff;}}
.t {{background:#a4262d;color:#fff;}}
.x {{background:#566171;color:#fff;}}
.g {{background:#d39b2d;color:#211a0c;}}
.legend {{color:#5f5a53;font-size:13px;margin-top:10px;}}
.stButton > button {{border-radius:12px;font-weight:800;min-height:44px;}}

/* Make main Streamlit controls readable too */
div[data-baseweb="select"] > div {{background:#fff !important;}}
div[data-baseweb="select"] span {{color:#182235 !important;}}
</style>
""",
unsafe_allow_html=True,
)

# ---------- Environment state ----------
if "env" not in st.session_state:
    st.session_state.env = ChakravyuhaEnvironment()

env = st.session_state.env

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ⚔️ CHAKRAVYUHA")
    st.caption("Strategic AI Lab • Member 2 Environment")

    scenarios = ["infiltration", "reconnaissance", "escape"]
    info_levels = ["LOW", "MEDIUM", "HIGH"]
    difficulties = ["LOW", "MEDIUM", "HIGH"]

    scenario = st.selectbox("SCENARIO", scenarios, index=scenarios.index(env.scenario))
    information = st.selectbox("INFORMATION ACCESS", info_levels,
                               index=info_levels.index(env.information))
    difficulty = st.selectbox("DIFFICULTY", difficulties,
                              index=difficulties.index(env.difficulty))
    decision_mode = st.selectbox("DECISION MODE", ["Manual", "AI Agent"])

    if st.button("↻ RESET SIMULATION", use_container_width=True):
        st.session_state.env = ChakravyuhaEnvironment(
            scenario, information, difficulty
        )
        st.rerun()

if (env.scenario, env.information, env.difficulty) != (
    scenario, information, difficulty
):
    st.session_state.env = ChakravyuhaEnvironment(
        scenario, information, difficulty
    )
    env = st.session_state.env

obs = env.get_observation()

# ---------- Header ----------
st.markdown(
"""
<div class="hero">
  <div class="eyebrow">THE KURUKSHETRA DECISION LAB</div>
  <div class="hero-title">CHAKRAVYUHA</div>
  <div class="hero-sub">
    Decision-making under incomplete information • layered environment •
    dynamic threats • explainable uncertainty
  </div>
</div>
""",
unsafe_allow_html=True,
)

# ---------- Metrics ----------
layer = "INNER CORE" if obs["agent"][0] <= 4 else "BOUNDARY"
metrics = [
    ("LAYER", layer),
    ("STEP", obs["step"]),
    ("TOTAL REWARD", f'{obs["total_reward"]:.1f}'),
    ("VISIBLE THREATS", obs["visible_threats"]),
    ("UNCERTAINTY", f'{obs["uncertainty"]:.1f}%'),
]
cols = st.columns(5)
for col, (label, value) in zip(cols, metrics):
    col.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div></div>',
        unsafe_allow_html=True,
    )

# ---------- Grid renderer ----------
def render_grid(grid):
    classes = {
        "?": ("u", "?"), ".": ("e", "·"), "P": ("p", "P"),
        "E": ("t", "E"), "X": ("x", "X"), "G": ("g", "G")
    }
    html = ['<div class="world">']
    for row in grid:
        for value in row:
            css, text = classes.get(value, ("u", "?"))
            html.append(f'<div class="cell {css}">{text}</div>')
    html.append("</div>")
    return "".join(html)

# ---------- Main tabs ----------
t1, t2, t3, t4 = st.tabs(["⚔️ LIVE BREACH", "🧠 INTELLIGENCE MAP",
                          "🔬 RESEARCH MODE", "📊 EVALUATION"])

with t1:
    left, right = st.columns([1.25, 0.9], gap="large")

    with left:
        st.markdown('<div class="section-title">Agent\'s Partial World</div>',
                    unsafe_allow_html=True)
        st.markdown(render_grid(obs["grid"]), unsafe_allow_html=True)
        st.markdown(
            '<div class="legend">P = agent • E = observed threat • X = barrier • '
            'G = visible core • ? = unknown • · = known empty cell</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="section-title">Mission Control</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="panel">
              <b>Objective:</b> breach inner core at <code>{obs["goal"]}</code><br><br>
              <b>Current position:</b> <code>{obs["agent"]}</code><br><br>
              <b>Known area:</b> {100-obs["uncertainty"]:.1f}%<br>
              <b>Hidden threats:</b> {obs["hidden_threats"]}<br>
              <b>Intel scans:</b> {obs["scans"]}<br><br>
              <b>Event:</b> {obs["last_event"].replace("_"," ")}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("#### Choose action")

    if decision_mode == "Manual":
        action = st.selectbox("Action", obs["valid_actions"],
                              label_visibility="collapsed")
        c1, c2 = st.columns(2)

        if c1.button("▶ EXECUTE NEXT ACTION", type="primary",
                     use_container_width=True):
            env.step(action)
            st.rerun()

        if c2.button("↻ RESET", use_container_width=True):
            st.session_state.env = ChakravyuhaEnvironment(
                scenario, information, difficulty
            )
            st.rerun()
    else:
        # Member 1's decision engine. A fresh agent (empty memory) is created
        # whenever the environment is reset or its settings change.
        if st.session_state.get("agent_env") is not env:
            st.session_state.agent = SmartChakravyuhaAgent()
            st.session_state.agent_env = env
            st.session_state.decision = None
        agent = st.session_state.agent

        if obs["terminal"]:
            st.info("Episode finished. Reset the simulation to run the AI agent again.")
        else:
            # choose_action() updates the agent's memory, so ask only once per
            # step (Streamlit reruns this script on every click).
            decision = st.session_state.get("decision")
            if not decision or decision["step"] != obs["step"]:
                action, scores = agent.choose_action(obs)
                decision = {"step": obs["step"], "action": action, "scores": scores}
                st.session_state.decision = decision

            st.success(f"AI decision: **{decision['action']}**")
            ranked = sorted(decision["scores"].items(), key=lambda kv: -kv[1])
            st.caption(
                "Reasoning: the agent scores every valid action from what it can "
                "see (goal progress, visible threats, unknown cells, places "
                "already visited or scanned) and picks the highest score."
            )
            st.table([{"Action": a, "Score": sc,
                       "Chosen": "✔" if a == decision["action"] else ""}
                      for a, sc in ranked])

            c1, c2 = st.columns(2)
            if c1.button("🤖 EXECUTE AI ACTION", type="primary",
                         use_container_width=True):
                env.step(decision["action"])
                st.rerun()
            if c2.button("⏩ RUN TO END", use_container_width=True):
                action = decision["action"]
                while True:
                    o = env.step(action)
                    if o["terminal"]:
                        break
                    action, _ = agent.choose_action(o)
                st.rerun()

    if obs["terminal"]:
        if obs["success"]:
            st.success("🏆 CORE BREACHED — MISSION SUCCESS")
        else:
            st.error("⚠️ MISSION ENDED — " +
                     obs["last_event"].replace("_"," ").upper())

with t2:
    st.markdown('<div class="section-title">Intelligence Map</div>',
                unsafe_allow_html=True)
    st.info(
        "The decision agent sees only the revealed portion of the world. "
        "SCAN expands the information frontier."
    )
    st.markdown(render_grid(obs["grid"]), unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric("Known area", f'{100-obs["uncertainty"]:.1f}%')
    b.metric("Visible threats", obs["visible_threats"])
    c.metric("Hidden threats", obs["hidden_threats"])
    st.write("**Available actions:** " + ", ".join(obs["valid_actions"]))

with t3:
    st.markdown('<div class="section-title">Research / Ground Truth</div>',
                unsafe_allow_html=True)
    st.warning(
        "Ground truth is intentionally hidden from the decision agent and shown "
        "here only for evaluation/debugging."
    )
    st.markdown(render_grid(env.true_world()), unsafe_allow_html=True)
    truth = env.ground_truth()
    st.code(
        f"Enemies: {truth['enemies']}\n"
        f"Obstacles: {truth['obstacles']}\n"
        f"Agent: {truth['agent']}\n"
        f"Goal: {truth['goal']}\n"
        f"Step: {truth['step']}"
    )

with t4:
    st.markdown('<div class="section-title">Evaluation Results</div>',
                unsafe_allow_html=True)
    results_dir = Path(__file__).parent / "evaluation" / "results"
    summary_file = results_dir / "summary_by_agent.csv"
    if not summary_file.exists():
        st.info("No results yet. Run:  python -m evaluation.experiments")
    else:
        with open(summary_file, newline="") as f:
            rows = list(csv.DictReader(f))
        st.caption(
            f"Each agent was run for {rows[0]['episodes']} episodes across every "
            "scenario, information level and difficulty."
        )
        columns = [("agent", "Agent"), ("success_rate", "Success %"),
                   ("defeat_rate", "Defeat %"), ("timeout_rate", "Timeout %"),
                   ("avg_reward", "Avg reward"), ("avg_steps", "Avg steps"),
                   ("avg_scans", "Avg scans")]
        st.table([{label: r[key] for key, label in columns} for r in rows])

        g1, g2 = st.columns(2)
        graphs = [("success_rate.png", g1), ("avg_reward.png", g2),
                  ("success_vs_difficulty.png", g1),
                  ("success_vs_information.png", g2), ("avg_steps.png", g1)]
        for name, col in graphs:
            if (results_dir / name).exists():
                col.image(str(results_dir / name), use_container_width=True)

st.divider()
st.caption(
    "Environment: state, scenarios, partial observability, rewards • "
    "AI agent: score-based decision engine • "
    "Evaluation: experiments, metrics and graphs"
)
