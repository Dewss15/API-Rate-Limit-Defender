# API Rate Limit Defender - Unified Agent README

This README is a single guide for all defender agents in this repository:

- Easy agent
- Medium agent
- Hard agent

It also includes run commands, expected behavior, and file mapping.

## 1. Agent Files

Core agent logic files:

- `easy_defender_agent.py`
- `medium_defender_agent.py`
- `hard_defender_agent.py`

Demo entrypoints:

- `easy_agent_demo.py`
- `medium_agent_demo.py`
- `hard_agent_demo.py`

Environment and evaluation files used by all agents:

- `environment.py`
- `data.py`
- `evaluator.py`
- `models.py`

## 2. Dataset Mapping

- Easy agent: uses `get_easy_data()`
- Medium agent: uses `get_medium_data()`
- Hard agent: uses `get_winning_data()` and validates on `get_extreme_data()`

## 3. How To Run

Open terminal in repo root:

```bash
cd API-Rate-Limit-Defender
```

Run each agent demo:

```bash
python easy_agent_demo.py
python medium_agent_demo.py
python hard_agent_demo.py
```

Run environment tests:

```bash
python test_environment.py
```

## 4. What Each Agent Does

### EasyDefenderAgent

- Goal: simple baseline for obvious bot patterns
- Main behavior: blocks clear high-risk users with straightforward deterministic logic
- Output: per-episode metrics plus TP/FP/FN report

### MediumDefenderAgent

- Goal: handle overlap between humans and bots in medium data
- Main behavior: combines suspicious pattern, RPS, and tier guardrails
- Output: 100-episode training log plus TP/FP/FN report

### HardDefenderAgent

- Goal: handle traps and mixed bot behaviors in hard data
- Main behavior: risk-scoring policy using multiple clues, premium protection, and deterministic selection
- Output: 200-episode training log, stability report, and TP/FP/FN user-id report

## 5. Common Output Terms

- TP: bot correctly blocked
- FP: real user wrongly blocked
- FN: bot missed
- F1: harmonic mean of precision and recall
- System health: `1 - ((FN + FP) / total_users)`

## 6. Determinism

All three defender agents are deterministic:

- no random action selection during policy decisions
- same input dataset -> same result each run

## 7. Typical Workflow

1. Verify environment:

```bash
python test_environment.py
```

2. Run easy baseline:

```bash
python easy_agent_demo.py
```

3. Run medium agent:

```bash
python medium_agent_demo.py
```

4. Run hard agent:

```bash
python hard_agent_demo.py
```

5. Compare F1, FP count, and system health across agents.

## 8. Note About Running From Parent Folder

If you run a demo from the parent folder instead of repo root, Python may fail to find local modules.
Always run from inside the repository folder (`API-Rate-Limit-Defender`).
