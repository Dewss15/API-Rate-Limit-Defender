"""
API Rate Limit Defender — Live SOC Dashboard
=============================================
Streamlit UI for the Meta x Scaler OpenEnv Hackathon 2026
Team Capillaries

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
from collections import deque

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="API Rate Limit Defender",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DARK SOC THEME  (colors unchanged)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    background-color: #080c14 !important;
    color: #c9d1d9 !important;
    font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid #1f2937 !important;
}
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%) !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    padding: 12px !important;
}
[data-testid="metric-container"] label {
    color: #58a6ff !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1.8rem !important;
    color: #e6edf3 !important;
}
h1, h2, h3 {
    font-family: 'Rajdhani', sans-serif !important;
    color: #58a6ff !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid #1e3a5f !important;
    border-radius: 6px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1e3a5f, #0d2137) !important;
    color: #58a6ff !important;
    border: 1px solid #58a6ff !important;
    border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.08em !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #58a6ff !important;
    color: #0d1117 !important;
}
.stSelectbox > div > div {
    background-color: #111827 !important;
    border: 1px solid #1e3a5f !important;
    color: #c9d1d9 !important;
}
.stProgress > div > div { background-color: #1e3a5f !important; }
.stProgress > div > div > div {
    background: linear-gradient(90deg, #58a6ff, #3fb950) !important;
}
.stAlert { border-radius: 6px !important; font-family: 'Share Tech Mono', monospace !important; }
hr { border-color: #1e3a5f !important; }

/* Structured feed cards */
.feed-card {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    background: #0d1117;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
    border-left: 3px solid #1e3a5f;
    line-height: 1.7;
}
.feed-card-block   { border-left-color: #f85149; }
.feed-card-allow   { border-left-color: #3fb950; }
.feed-card-premium { border-left-color: #bc8cff; }

/* Explainability panel */
.explain-panel {
    background: linear-gradient(135deg, #0d1117, #111827);
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 14px 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.9;
}

/* Header */
.header-bar {
    background: linear-gradient(90deg, #0d1117, #111827);
    border-bottom: 2px solid #1e3a5f;
    padding: 16px 0 12px 0;
    margin-bottom: 8px;
}
.header-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem; font-weight: 700;
    color: #58a6ff; letter-spacing: 0.1em;
}
.header-desc {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem; color: #c9d1d9;
    margin-top: 4px; opacity: 0.85;
}
.header-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem; color: #8b949e;
    letter-spacing: 0.12em; margin-top: 6px;
}
.status-live {
    display: inline-block;
    width: 8px; height: 8px;
    background: #3fb950; border-radius: 50%;
    margin-right: 6px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%   { opacity: 1; }
    50%  { opacity: 0.3; }
    100% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA GENERATORS  (mirrors data.py — unchanged)
# ─────────────────────────────────────────────

def generate_users(n_users, n_bots, n_premium, seed=42):
    """Generate a deterministic user dataset."""
    rng = random.Random(seed)
    users = []

    for i in range(n_bots):
        rps = round(rng.uniform(8.0, 20.0), 2)
        users.append({
            "user_id": f"BOT_{i+1:03d}", "tier": "normal",
            "rps": rps, "is_bot": True, "is_premium": False,
            "behavior_flag": rng.choice([True, True, False]),
        })
    for i in range(n_premium):
        rps = round(rng.uniform(3.0, 9.0), 2)
        users.append({
            "user_id": f"VIP_{i+1:03d}", "tier": "premium",
            "rps": rps, "is_bot": False, "is_premium": True,
            "behavior_flag": False,
        })
    n_normal = n_users - n_bots - n_premium
    for i in range(n_normal):
        rps = round(rng.uniform(0.5, 5.0), 2)
        users.append({
            "user_id": f"USR_{i+1:03d}", "tier": "normal",
            "rps": rps, "is_bot": False, "is_premium": False,
            "behavior_flag": False,
        })

    rng.shuffle(users)
    return users


DATASETS = {
    "🟢 Easy Triage      (10 users)": {"n_users": 10, "n_bots": 3,  "n_premium": 2,  "seed": 42},
    "🟡 Behavioral       (20 users)": {"n_users": 20, "n_bots": 6,  "n_premium": 4,  "seed": 43},
    "🟠 Extreme          (40 users)": {"n_users": 40, "n_bots": 12, "n_premium": 8,  "seed": 44},
    "🔴 Adversarial      (83 users)": {"n_users": 83, "n_bots": 25, "n_premium": 17, "seed": 45},
}


# ─────────────────────────────────────────────
# AGENT LOGIC  (mirrors hard_defender.py — unchanged)
# ─────────────────────────────────────────────

def compute_risk_score(user):
    """Deterministic risk score in [0.0, 1.0]."""
    rps_ratio  = min(user["rps"] / 20.0, 1.0)
    behav_flag = 0.3 if user["behavior_flag"] else 0.0
    return round(0.6 * rps_ratio + 0.4 * behav_flag, 4)


def build_human_reason(user, action, risk, eff_th):
    """
    Plain-English reason derived from agent features.
    All logic sourced from actual user data — no manual overrides.
    """
    if action == "BLOCK":
        parts = []
        if user["behavior_flag"]:
            parts.append("suspicious request pattern")
        if user["rps"] >= 10.0:
            parts.append(f"high RPS ({user['rps']})")
        elif user["rps"] >= 7.0:
            parts.append(f"elevated RPS ({user['rps']})")
        if not parts:
            parts.append(f"risk {risk:.3f} ≥ threshold {eff_th:.2f}")
        return "Blocked — " + " + ".join(parts)
    else:
        if user["is_premium"]:
            return f"Allowed — premium user (protected threshold: {eff_th:.2f})"
        if not user["behavior_flag"] and user["rps"] < 5.0:
            return f"Allowed — normal behavior, low RPS ({user['rps']})"
        return f"Allowed — risk {risk:.3f} < threshold {eff_th:.2f}"


def compute_confidence(risk, eff_th):
    """Margin from decision boundary → confidence label + color."""
    margin = abs(risk - eff_th)
    if   margin >= 0.30: return "High",   "#3fb950"
    elif margin >= 0.12: return "Medium",  "#d29922"
    else:                return "Low",     "#f85149"


def agent_decision(user, rps_threshold=0.50):
    """
    Risk-aware decision engine.
    Returns: (action, risk, human_reason, effective_threshold)
    """
    risk   = compute_risk_score(user)
    eff_th = rps_threshold + (0.30 if user["tier"] == "premium" else 0.0)
    action = "BLOCK" if risk >= eff_th else "ALLOW"
    reason = build_human_reason(user, action, risk, eff_th)
    return action, risk, reason, eff_th


def score_episode(users, decisions):
    """Deterministic F1-based scorer — logic unchanged."""
    blocked  = {u["user_id"] for u, d in zip(users, decisions) if d == "BLOCK"}
    gt_bots  = {u["user_id"] for u in users if u["is_bot"]}
    gt_legit = {u["user_id"] for u in users if not u["is_bot"]}
    premium  = {u["user_id"] for u in users if u["is_premium"]}

    tp = len(blocked & gt_bots)
    fp = len(blocked & gt_legit)
    fn = len(gt_bots - blocked)
    tn = len(gt_legit - blocked)
    total = tp + fp + fn + tn

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)
    accuracy  = (tp + tn) / total if total > 0 else 0.0

    premium_errors = len(blocked & premium)
    prem_penalty   = 0.1 * premium_errors / max(len(premium), 1)
    final_score    = max(0.0, f1 - prem_penalty)

    return {
        "f1": round(f1, 3), "precision": round(precision, 3),
        "recall": round(recall, 3), "accuracy": round(accuracy, 3),
        "score": round(final_score, 3),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "premium_errors": premium_errors, "blocked_count": len(blocked),
    }


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

def init_state():
    defaults = {
        "running": False, "paused": False, "step_idx": 0,
        "users": [], "decisions": [], "risk_scores": [],
        "reasons": [], "eff_thresholds": [],
        "event_log": deque(maxlen=30), "metrics": {},
        "dataset_key": list(DATASETS.keys())[0],
        "threshold": 0.50, "done": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────
# HEADER  (+ one-line system description)
# ─────────────────────────────────────────────

st.markdown("""
<div class="header-bar">
  <div class="header-title">🛡️ API RATE LIMIT DEFENDER</div>
  <div class="header-desc">
    Real-time API defense system that classifies users based on behavioral risk
    and blocks malicious traffic — while protecting legitimate and premium users.
  </div>
  <div class="header-sub">
    <span class="status-live"></span>
    LIVE THREAT MONITORING &nbsp;·&nbsp; META × SCALER OPENENV HACKATHON 2026
    &nbsp;·&nbsp; TEAM CAPILLARIES
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR — CONTROLS
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ SIMULATION CONTROLS")
    st.markdown("---")

    dataset_key = st.selectbox("🗂️ Select Dataset", list(DATASETS.keys()))
    threshold   = st.slider(
        "🎯 Block Threshold", min_value=0.30, max_value=0.80,
        value=0.50, step=0.05,
        help="Users with risk score above this are blocked. Lower = stricter.",
    )
    speed = st.slider(
        "⚡ Sim Speed", min_value=0.05, max_value=0.60,
        value=0.18, step=0.05, format="%.2f s/step",
    )

    st.markdown("---")
    col_s, col_p = st.columns(2)
    with col_s: start_btn = st.button("▶ START", use_container_width=True)
    with col_p: pause_btn = st.button("⏸ PAUSE", use_container_width=True)
    reset_btn = st.button("↺ RESET", use_container_width=True)

    st.markdown("---")
    st.markdown("### 📖 HOW RISK IS CALCULATED")
    st.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.74rem;
            color:#8b949e;line-height:2.1;">
<b style="color:#58a6ff;">Step 1 — Risk Score (0 to 1)</b><br>
risk = 0.6 × (rps ÷ 20)<br>
&nbsp;&nbsp;&nbsp;&nbsp; + 0.4 × suspicious_pattern<br><br>
<b style="color:#58a6ff;">Step 2 — Block Threshold</b><br>
Normal user &nbsp; → block if risk ≥ 0.50<br>
Premium user → block if risk ≥ 0.80<br><br>
<b style="color:#58a6ff;">Step 3 — Final Score</b><br>
F1 − penalty for premium errors
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
<div style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;color:#8b949e;">
· Team Capillaries · OpenEnv 0.1 Compliant
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONTROL LOGIC
# ─────────────────────────────────────────────

if reset_btn:
    cfg = DATASETS[dataset_key]
    st.session_state.users         = generate_users(**cfg)
    st.session_state.decisions     = []
    st.session_state.risk_scores   = []
    st.session_state.reasons       = []
    st.session_state.eff_thresholds= []
    st.session_state.event_log     = deque(maxlen=30)
    st.session_state.step_idx      = 0
    st.session_state.metrics       = {}
    st.session_state.running       = False
    st.session_state.paused        = False
    st.session_state.done          = False
    st.session_state.dataset_key   = dataset_key
    st.session_state.threshold     = threshold

if start_btn and not st.session_state.done:
    if not st.session_state.users:
        cfg = DATASETS[dataset_key]
        st.session_state.users       = generate_users(**cfg)
        st.session_state.dataset_key = dataset_key
        st.session_state.threshold   = threshold
    st.session_state.running = True
    st.session_state.paused  = False

if pause_btn:
    st.session_state.paused = not st.session_state.paused


# ─────────────────────────────────────────────
# LAYOUT — 3 COLUMNS
# ─────────────────────────────────────────────

col_left, col_mid, col_right = st.columns([1.1, 1.5, 1.4])

users     = st.session_state.users
decisions = st.session_state.decisions
n_total   = len(users)
n_proc    = len(decisions)
n_blocked = decisions.count("BLOCK")
n_allowed = decisions.count("ALLOW")
m         = st.session_state.metrics


# ── LEFT: METRICS + WHY THIS DECISION ────────
with col_left:

    st.markdown("### 📡 LIVE METRICS")
    st.metric("USERS PROCESSED", f"{n_proc} / {n_total}")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("F1 SCORE",  f"{m['f1']}"        if m else "—",
                  help="Balance between catching bots and not blocking legit users")
        st.metric("PRECISION", f"{m['precision']}"  if m else "—",
                  help="Of all blocked users, what % were actually bots?")
    with c2:
        st.metric("RECALL",    f"{m['recall']}"     if m else "—",
                  help="Of all bots, what % did we catch?")
        st.metric("ACCURACY",  f"{m['accuracy']}"   if m else "—",
                  help="Overall correct decisions across all users")

    st.markdown("---")
    st.markdown("### 📊 SCAN PROGRESS")
    prog = n_proc / n_total if n_total > 0 else 0
    st.progress(prog)
    st.markdown(
        f"<div style='font-family:Share Tech Mono,monospace;font-size:0.73rem;"
        f"color:#8b949e;margin-top:4px;'>{prog*100:.1f}% of users scanned</div>",
        unsafe_allow_html=True
    )

    c3, c4, c5 = st.columns(3)
    c3.metric("🔴 Blocked",  n_blocked)
    c4.metric("🟢 Allowed",  n_allowed)
    c5.metric("💎 Prem Err", m.get("premium_errors", 0) if m else 0)

    # ── WHY THIS DECISION? ──────────────────
    st.markdown("---")
    st.markdown("### 🔍 WHY THIS DECISION?")

    if not decisions:
        st.markdown(
            "<div class='explain-panel' style='color:#8b949e;'>"
            "Start the simulation — then select any user to see why the agent made its decision."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        processed_ids = [users[i]["user_id"] for i in range(n_proc)]
        sel_id  = st.selectbox("Inspect a user", processed_ids, key="inspect_select")
        sel_idx = processed_ids.index(sel_id)

        su      = users[sel_idx]
        s_act   = decisions[sel_idx]
        s_risk  = st.session_state.risk_scores[sel_idx]
        s_rsn   = st.session_state.reasons[sel_idx]
        s_eff   = st.session_state.eff_thresholds[sel_idx]
        conf_l, conf_c = compute_confidence(s_risk, s_eff)

        a_color = "#f85149" if s_act == "BLOCK" else "#3fb950"
        a_icon  = "🔴" if s_act == "BLOCK" else "🟢"
        tier_s  = "💎 Premium" if su["is_premium"] else "👤 Normal"
        susp_s  = "⚠️ Yes — non-human pattern detected" if su["behavior_flag"] else "✅ No"
        rps_contrib  = round(0.6 * min(su["rps"] / 20.0, 1.0), 4)
        flag_contrib = 0.3 if su["behavior_flag"] else 0.0

        st.markdown(f"""
<div class="explain-panel">
  <div style="font-size:1.05rem;font-weight:700;color:{a_color};margin-bottom:6px;">
    {a_icon} {s_act} — {su['user_id']}
  </div>
  <div style="color:#8b949e;font-size:0.72rem;margin-bottom:10px;">{s_rsn}</div>

  <div style="margin-bottom:4px;">
    <span style="color:#58a6ff;">Risk Score</span>
    <span style="color:#e6edf3;margin-left:8px;">{s_risk:.4f}</span>
    &nbsp;vs&nbsp;
    <span style="color:#58a6ff;">Threshold</span>
    <span style="color:#e6edf3;margin-left:8px;">{s_eff:.2f}</span>
  </div>
  <div style="margin-bottom:10px;">
    <span style="color:#58a6ff;">Confidence</span>
    <span style="color:{conf_c};margin-left:8px;">{conf_l}</span>
    <span style="color:#8b949e;font-size:0.68rem;margin-left:6px;">
      (margin = {abs(s_risk - s_eff):.3f})
    </span>
  </div>

  <hr style="border-color:#1e3a5f;margin:6px 0 8px 0;">
  <div style="color:#58a6ff;margin-bottom:4px;">Key Factors</div>
  <div style="color:#8b949e;margin-left:6px;">
    • Request Rate (RPS):
    <span style="color:#e6edf3;">{su['rps']} req/s</span>
    <span style="color:#8b949e;font-size:0.68rem;"> → risk contribution: {rps_contrib}</span>
  </div>
  <div style="color:#8b949e;margin-left:6px;">
    • Suspicious Pattern:
    <span style="color:#e6edf3;">{susp_s}</span>
    <span style="color:#8b949e;font-size:0.68rem;"> → risk contribution: {flag_contrib}</span>
  </div>
  <div style="color:#8b949e;margin-left:6px;">
    • User Tier: <span style="color:#e6edf3;">{tier_s}</span>
    {'<span style="color:#bc8cff;font-size:0.68rem;"> → threshold raised by +0.30</span>'
     if su["is_premium"] else ""}
  </div>
</div>
""", unsafe_allow_html=True)


# ── MIDDLE: LIVE FEED ────────────────────────
with col_mid:
    st.markdown("### 🔴 LIVE DECISION FEED")
    st.markdown(
        "<div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;"
        "color:#8b949e;margin-bottom:8px;'>"
        "Every card shows what decision was made and why, in plain English."
        "</div>",
        unsafe_allow_html=True,
    )

    feed_placeholder  = st.empty()
    chart_placeholder = st.empty()

    def render_feed():
        logs = list(st.session_state.event_log)
        if not logs:
            feed_placeholder.info("⏳ Press ▶ START to begin the simulation.")
            return

        html = ""
        for entry in reversed(logs[-12:]):
            ts     = entry["ts"]
            uid    = entry["uid"]
            action = entry["action"]
            risk   = entry["risk"]
            reason = entry["reason"]
            tier   = entry["tier"]
            eff_th = entry["eff_th"]

            if action == "BLOCK":
                cls     = "feed-card-block"
                icon    = "🔴"
                ac_col  = "#f85149"
                verdict = "BLOCKED"
                cmp_html = (f"<span style='color:#f85149;'>"
                            f"risk {risk:.3f} ≥ threshold {eff_th:.2f}</span>")
            elif tier == "premium":
                cls     = "feed-card-premium"
                icon    = "💎"
                ac_col  = "#bc8cff"
                verdict = "ALLOWED (PREMIUM)"
                cmp_html = (f"<span style='color:#bc8cff;'>"
                            f"risk {risk:.3f} &lt; threshold {eff_th:.2f}</span>")
            else:
                cls     = "feed-card-allow"
                icon    = "🟢"
                ac_col  = "#3fb950"
                verdict = "ALLOWED"
                cmp_html = (f"<span style='color:#3fb950;'>"
                            f"risk {risk:.3f} &lt; threshold {eff_th:.2f}</span>")

            html += f"""
<div class="feed-card {cls}">
  <div style="display:flex;justify-content:space-between;">
    <span style="color:#8b949e;">[{ts}]</span>
    <span style="color:{ac_col};font-weight:700;">{icon} {verdict}</span>
  </div>
  <div style="color:#e6edf3;font-weight:600;">{uid}</div>
  <div style="color:#8b949e;">{cmp_html}</div>
  <div style="color:#c9d1d9;font-size:0.72rem;margin-top:2px;">↳ {reason}</div>
</div>"""

        feed_placeholder.markdown(html, unsafe_allow_html=True)

    render_feed()

    if st.session_state.risk_scores:
        st.markdown("### 📈 RISK SCORE DISTRIBUTION")
        st.markdown(
            "<div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;"
            "color:#8b949e;margin-bottom:4px;'>"
            "Bars crossing the 0.50 threshold indicate high-risk users flagged for blocking."
            "</div>",
            unsafe_allow_html=True,
        )
        chart_data = pd.DataFrame({
            "User": [users[i]["user_id"] for i in range(n_proc)],
            "Risk": st.session_state.risk_scores,
        })
        chart_placeholder.bar_chart(
            chart_data.set_index("User")["Risk"],
            use_container_width=True, height=200,
        )


# ── RIGHT: USER DECISIONS TABLE ──────────────
with col_right:
    st.markdown("### 👥 USER DECISIONS")
    st.markdown(
        "<div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;"
        "color:#8b949e;margin-bottom:8px;'>"
        "All decisions come directly from the agent's risk engine — no manual overrides."
        "</div>",
        unsafe_allow_html=True,
    )

    table_placeholder = st.empty()

    def render_table():
        if not decisions:
            table_placeholder.info("No decisions yet. Press ▶ START.")
            return

        rows = []
        for i, (u, d) in enumerate(zip(users[:n_proc], decisions)):
            risk = st.session_state.risk_scores[i]

            # Short, human-readable reason derived from actual features
            if d == "BLOCK":
                short = (
                    "High RPS + suspicious pattern" if u["behavior_flag"] and u["rps"] >= 8.0
                    else "High request rate"         if u["rps"] >= 10.0
                    else "Risk score above threshold"
                )
            else:
                short = (
                    "Premium — protected threshold" if u["is_premium"]
                    else "Normal behavior, below threshold"
                )

            rows.append({
                "ID":       u["user_id"],
                "Tier":     "💎" if u["is_premium"] else "👤",
                "RPS":      u["rps"],
                "Risk":     risk,
                "Decision": "🔴 BLOCK" if d == "BLOCK" else "🟢 ALLOW",
                "Reason":   short,
            })

        df = pd.DataFrame(rows)
        table_placeholder.dataframe(
            df, use_container_width=True, height=500,
            hide_index=True,
            column_config={
                "RPS":    st.column_config.NumberColumn(format="%.2f"),
                "Risk":   st.column_config.NumberColumn(format="%.3f"),
                "Reason": st.column_config.TextColumn(width="large"),
            },
        )

    render_table()


# ─────────────────────────────────────────────
# SIMULATION LOOP  (backend logic unchanged)
# ─────────────────────────────────────────────

if st.session_state.running and not st.session_state.paused and not st.session_state.done:
    idx = st.session_state.step_idx

    if idx < len(st.session_state.users):
        user = st.session_state.users[idx]
        action, risk, reason, eff_th = agent_decision(user, st.session_state.threshold)

        st.session_state.decisions.append(action)
        st.session_state.risk_scores.append(risk)
        st.session_state.reasons.append(reason)
        st.session_state.eff_thresholds.append(eff_th)

        ts = datetime.now().strftime("%H:%M:%S")
        st.session_state.event_log.append({
            "ts": ts, "uid": user["user_id"], "action": action,
            "risk": risk, "reason": reason, "tier": user["tier"], "eff_th": eff_th,
        })

        st.session_state.step_idx += 1
        st.session_state.metrics = score_episode(
            st.session_state.users[:st.session_state.step_idx],
            st.session_state.decisions,
        )

        time.sleep(speed)
        st.rerun()

    else:
        st.session_state.running = False
        st.session_state.done    = True
        st.session_state.metrics = score_episode(
            st.session_state.users, st.session_state.decisions,
        )
        st.rerun()


# ─────────────────────────────────────────────
# FINAL RESULT CARD  (with interpreted verdict)
# ─────────────────────────────────────────────

if st.session_state.done and st.session_state.metrics:
    m  = st.session_state.metrics
    f1 = m["f1"]

    # Interpreted verdict based on F1 thresholds
    if f1 > 0.85:
        color   = "#3fb950"
        verdict = "🟢 Defense Successful — strong bot detection with minimal errors"
    elif f1 > 0.60:
        color   = "#58a6ff"
        verdict = "🔵 Good Performance — agent is working, some improvements possible"
    else:
        color   = "#d29922"
        verdict = "⚠️ Needs Improvement — too many missed bots or wrongly blocked users"

    # Key issue explanation
    if m["fp"] > m["fn"]:
        key_issue  = f"{m['fp']} legitimate user(s) were wrongly blocked (false positives) — threshold may be too low"
        iss_color  = "#f85149"
    elif m["fn"] > 0:
        key_issue  = f"{m['fn']} bot(s) slipped through undetected (false negatives) — threshold may be too high"
        iss_color  = "#d29922"
    else:
        key_issue  = "No significant errors detected — precision and recall are both strong"
        iss_color  = "#3fb950"

    prem_note = (
        f"⚠️ {m['premium_errors']} premium user(s) incorrectly blocked — heavy penalty applied to score."
        if m["premium_errors"] > 0
        else "✅ All premium users correctly protected — zero collateral damage."
    )
    prem_color = "#f85149" if m["premium_errors"] > 0 else "#3fb950"

    st.markdown("---")
    st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #0d1117, #111827);
    border: 2px solid {color};
    border-radius: 12px;
    padding: 24px 32px;
    margin-top: 16px;
">
  <div style="font-family:'Rajdhani',sans-serif;font-size:1.7rem;
              font-weight:700;color:{color};letter-spacing:0.08em;margin-bottom:4px;">
    SIMULATION COMPLETE
  </div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:1.15rem;
              color:#e6edf3;margin-bottom:20px;">
    {verdict}
  </div>

  <div style="display:flex;gap:36px;flex-wrap:wrap;margin-bottom:18px;">
    <div>
      <div style="font-family:'Share Tech Mono',monospace;color:#8b949e;font-size:0.7rem;">
        F1 SCORE <span style="color:#444;font-size:0.6rem;">(bot-catch balance)</span>
      </div>
      <div style="font-family:'Share Tech Mono',monospace;color:{color};font-size:2rem;">{m['f1']:.3f}</div>
    </div>
    <div>
      <div style="font-family:'Share Tech Mono',monospace;color:#8b949e;font-size:0.7rem;">
        PRECISION <span style="color:#444;font-size:0.6rem;">(of blocked = real bots)</span>
      </div>
      <div style="font-family:'Share Tech Mono',monospace;color:#e6edf3;font-size:2rem;">{m['precision']:.3f}</div>
    </div>
    <div>
      <div style="font-family:'Share Tech Mono',monospace;color:#8b949e;font-size:0.7rem;">
        RECALL <span style="color:#444;font-size:0.6rem;">(bots detected)</span>
      </div>
      <div style="font-family:'Share Tech Mono',monospace;color:#e6edf3;font-size:2rem;">{m['recall']:.3f}</div>
    </div>
    <div>
      <div style="font-family:'Share Tech Mono',monospace;color:#8b949e;font-size:0.7rem;">
        ACCURACY <span style="color:#444;font-size:0.6rem;">(all decisions)</span>
      </div>
      <div style="font-family:'Share Tech Mono',monospace;color:#e6edf3;font-size:2rem;">{m['accuracy']:.3f}</div>
    </div>
    <div>
      <div style="font-family:'Share Tech Mono',monospace;color:#8b949e;font-size:0.7rem;">
        TP / FP / FN <span style="color:#444;font-size:0.6rem;">(caught / wrong / missed)</span>
      </div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:2rem;">
        <span style="color:#3fb950;">{m['tp']}</span> /
        <span style="color:#f85149;">{m['fp']}</span> /
        <span style="color:#d29922;">{m['fn']}</span>
      </div>
    </div>
  </div>

  <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;
              color:{iss_color};margin-bottom:6px;">→ {key_issue}</div>
  <div style="font-family:'Share Tech Mono',monospace;font-size:0.78rem;
              color:{prem_color};">{prem_note}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 RUN AGAIN WITH DIFFERENT SETTINGS", use_container_width=True):
        for k in ["running","paused","step_idx","decisions","risk_scores",
                  "reasons","eff_thresholds","event_log","metrics","done","users"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
