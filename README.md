# API Rate Limit Defender

Deterministic (no-randomness) API abuse defender demo with:
- A simple OpenEnv-style environment (`environment.py`) and data model (`models.py`)
- A deterministic rule-based agent (`hard_defender_agent.py`) with strict premium protection
- A judge-friendly Streamlit dashboard (`app.py`) focused on explainability

## Quickstart

### 1) Run the dashboard

```bash
streamlit run app.py
```

Flow:
1. Go to **Simulator** and click **Start Simulation** (choose intensity + user count).
2. Then open **Decisions** to see the per-user *risk → decision → reason* table.
3. Open **Analytics** for precision/recall/F1, system health, and confusion-matrix charts.

> Note: importing `app.py` directly (without `streamlit run`) may print Streamlit warnings like `missing ScriptRunContext` — that’s expected.

### 2) Run tests

This repo includes a self-contained test runner:

```bash
python test_hard_agent.py
```

It validates:
- Risk scoring behavior (relative ordering)
- **Strict premium protection** (no premium user blocking)
- Dataset performance (easy/medium/extreme/winning)
- Edge cases + adversarial scenarios
- Determinism (same input → same output)

## Latest test results

From the last run in this workspace:
- `test_hard_agent.py`: **28 / 28 tests passed (100%)**
- Winning dataset: **F1 = 0.889**, **Premium violations = 0**

## Determinism & integration notes

- The environment stores full user data including `is_bot`, but observations exposed to the agent **exclude** `is_bot`.
- Reward and `system_health` are computed deterministically and aligned to the evaluator.
- The dashboard does **not** change backend logic; it only presents results with clearer UI/UX.
