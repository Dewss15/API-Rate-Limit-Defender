import streamlit as st
from environment import make_env
import random

# ----------------------------
# Generate fake API data
# ----------------------------
def generate_data():
    data = []
    for i in range(8):
        data.append({
            "id": f"user_{i}",
            "requests_per_second": random.randint(1, 100),
            "flagged": random.choice([True, False]),
            "user_type": random.choice(["normal", "premium"]),
            "is_bot": random.choice([True, False])  # hidden truth
        })
    return data


# ----------------------------
# Simple agent (for now)
# ----------------------------
def simple_agent(obs):
    for user in obs["users"]:
        if user["rps"] > 70 or user["is_suspicious_pattern"]:
            return {"type": "block", "user_id": user["id"]}
    return {"type": "noop"}


# ----------------------------
# UI START
# ----------------------------
st.title("🚀 API Defender Dashboard")

# Create environment once
if "env" not in st.session_state:
    st.session_state.env = make_env()
    st.session_state.obs = st.session_state.env.reset(generate_data())

obs = st.session_state.obs

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("📊 System Health")
st.write(obs["system_health"])

st.subheader("👥 Users")
st.json(obs["users"])

st.subheader("🚫 Blocked Users")
st.write(obs["blocked_users"])

# ----------------------------
# BUTTONS
# ----------------------------
if st.button("▶ Run Agent Step"):
    action = ml_agent(obs)
    obs, reward, done, info = st.session_state.env.step(action)

    st.session_state.obs = obs

    st.write("Action:", action)
    st.write("Reward:", reward)
    st.write("Info:", info)

    if done:
        st.warning("Episode finished!")

if st.button("🔄 Reset"):
    st.session_state.obs = st.session_state.env.reset(generate_data())