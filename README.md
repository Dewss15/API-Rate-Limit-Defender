🛡️ API Rate Limit Defender — Live SOC Dashboard

🚀 Meta x Scaler OpenEnv Hackathon 2026

Team Capillaries
👩‍💻 Dewpearl Gonsalves, Anchal, Sakshi

---

📌 Overview

API Rate Limit Defender is an intelligent, deterministic security system that detects and mitigates abusive API traffic using behavior-based risk scoring.

The system simulates real-world attack scenarios and demonstrates how an automated defense agent classifies users as malicious or legitimate, while ensuring premium users are protected.

---

🎯 Problem Statement

Modern APIs are vulnerable to:

- Bot attacks
- Request flooding (high RPS)
- Abuse patterns that mimic legitimate users

Traditional rate limiting is:

- Static
- Blind to behavior
- Prone to blocking genuine users

---

💡 Our Solution

We built a risk-aware defense system that:

- Analyzes user behavior (RPS + patterns)
- Assigns a risk score (0–1)
- Dynamically decides to ALLOW or BLOCK
- Adjusts thresholds for premium users

---

🧠 Core Logic

🔹 Risk Score Calculation

risk = 0.6 × (rps / 20) + 0.4 × suspicious_pattern

🔹 Decision Rule

- Normal user → BLOCK if risk ≥ threshold
- Premium user → BLOCK if risk ≥ (threshold + 0.30)

---

⚙️ Features

🛡️ Real-Time Defense Simulation

- Step-by-step user processing
- Live decision feed (ALLOW / BLOCK)
- Risk-based classification

🔍 Explainability Engine

- Every decision has a human-readable reason
- Displays:
  - Risk score
  - Threshold comparison
  - Key contributing factors

📊 Performance Metrics

- Precision
- Recall
- F1 Score
- Accuracy
- Premium protection penalty

🎮 Interactive Controls

- Multiple attack datasets (Easy → Adversarial)
- Adjustable block threshold
- Simulation speed control

---

🧪 Datasets

We use deterministic simulated datasets to ensure:

- Reproducibility
- Fair evaluation
- Controlled testing across difficulty levels

Scenarios include:

- Low traffic (Easy)
- Behavioral attacks (Medium)
- High-volume abuse (Extreme)
- Adversarial conditions (Winning)

---

🧱 System Design

User Data → Risk Scoring → Decision Engine → Evaluation Metrics
                          ↓
                     UI Visualization

- Deterministic agent logic
- No randomness in decisions
- Fully explainable pipeline

---

🖥️ UI Dashboard

The Streamlit-based SOC dashboard provides:

- 📡 Live metrics panel
- 🔴 Real-time decision feed
- 👥 User-level classification table
- 🔍 Explainability panel
- 📈 Risk score visualization

---

🏁 Evaluation Strategy

We evaluate performance using:

- True Positives (TP)
- False Positives (FP)
- False Negatives (FN)
- True Negatives (TN)

Final score is based on:

F1 Score − penalty for blocking premium users

---

▶️ How to Run

streamlit run streamlit_app.py

---

🧠 Key Highlights

- Deterministic and reproducible system
- Strong explainability (no black-box decisions)
- Premium user protection built-in
- Interactive and intuitive UI

---

🎯 Conclusion

This project demonstrates how intelligent, behavior-aware rate limiting can outperform traditional static approaches by:

- Improving attack detection
- Reducing false positives
- Providing transparent decision-making

---

📣 Team Capillaries

Built with 💙 for OpenEnv Hackathon 2026