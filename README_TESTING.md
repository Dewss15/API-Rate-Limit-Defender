# 🎯 API Rate Limit Defender - Testing Guide

## ✅ How to Test Your Environment

### Quick Test
```bash
python test_environment.py
```

This runs 5 comprehensive tests:
1. ✅ **Basic Environment Setup** - Verifies structure and `is_bot` is hidden
2. ✅ **Reward Calculation** - Tests rewards for blocking bots/humans/premium
3. ✅ **Metrics Alignment** - Compares environment metrics with evaluator
4. ✅ **System Health Calculation** - Verifies health formula
5. ✅ **Simple Agent Execution** - Runs a full episode with a heuristic agent

### Example Usage
```bash
python example_usage.py
```

This shows 3 different agent strategies:
- **Heuristic Agent** - Same logic as your original test.py
- **Smart Agent** - Uses adaptive RPS threshold
- **Conservative Agent** - High precision, low recall

---

## 📂 Files Created

### Core Implementation
- **`models.py`** - User class and data models
  - `User` dataclass with all 5 attributes
  - `to_observation_dict()` excludes `is_bot` from agent view
  - `Observation` and `StepInfo` for type safety

- **`environment.py`** - OpenEnv-compatible RL environment
  - `reset(dataset)` - Initialize environment with user data
  - `step(action)` - Execute block actions and calculate rewards
  - Deterministic, no randomness
  - Integrates perfectly with your evaluator

### Testing Files
- **`test_environment.py`** - Comprehensive test suite
- **`example_usage.py`** - Example agents for comparison

---

## 🔧 Environment Specification

### Observation (what agent sees)
```python
{
    "users": [
        {
            "id": str,
            "rps": int,
            "is_suspicious_pattern": bool,
            "tier": str  # "normal" | "premium"
            # NOTE: is_bot is HIDDEN
        }
    ],
    "blocked_users": [list of user IDs],
    "system_health": float  # 0 to 1
}
```

### Action
```python
{
    "type": "block",
    "user_id": str
}
```

### Rewards
- **+0.4** - Correctly block a bot
- **-0.5** - Incorrectly block a human
- **+0.1** - Bonus if system_health > 0.8
- **-0.1** - Invalid action or already blocked

### Info Dictionary (matches evaluator)
```python
{
    "tp": int,           # True positives
    "fp": int,           # False positives
    "fn": int,           # False negatives
    "tn": int,           # True negatives
    "premium_penalty": int,  # Premium humans blocked this step
    "blocked_ids": [list of all blocked user IDs]
}
```

### System Health
```python
system_health = max(0, 1 - ((FN + FP) / total_users))
```

### Episode Termination
Episode ends when:
- `system_health <= 0` OR
- `steps >= 20`

---

## 🚀 Integration with Team

### For Agent (Sakshi)
```python
from environment import make_env
from data import get_winning_data

# Create environment
env = make_env()
data = get_winning_data()

# Initialize
obs = env.reset(data)

# Agent receives clean JSON without is_bot
# Must infer bots from: rps, is_suspicious_pattern, tier

# Take actions
action = {"type": "block", "user_id": "U42"}
obs, reward, done, info = env.step(action)
```

### For Evaluator (Anchal)
```python
from evaluator import evaluate

# After episode completes, use info["blocked_ids"]
results = evaluate(info["blocked_ids"], data)

# Results match environment metrics:
# results["TP"] == info["tp"]
# results["FP"] == info["fp"]
# results["FN"] == info["fn"]
```

---

## ✅ Key Features

✔️ **Deterministic** - No randomness, fully reproducible  
✔️ **Clean observations** - `is_bot` hidden from agent  
✔️ **Metric alignment** - Matches evaluator exactly  
✔️ **Premium penalty tracking** - Separate from FP count  
✔️ **Action-based rewards** - Immediate feedback  
✔️ **System health** - Same formula as evaluator  
✔️ **OpenEnv compatible** - Standard RL environment interface  

---

## 🐛 Troubleshooting

### If tests fail:
1. Check that `data.py` and `evaluator.py` are in the same directory
2. Ensure Python 3.7+ is installed
3. Run `python test_environment.py` to see detailed error messages

### If metrics don't match evaluator:
- The environment calculates TP/FP/FN/TN the same way as the evaluator
- System health uses: `1 - ((FN + FP) / total_users)`
- Premium penalty is tracked separately (not double-counted in FP)

---

## 💡 Tips for RL Training

1. **Start simple** - Test with `get_easy_data()` first
2. **Monitor health** - Episode ends if health <= 0
3. **Premium users** - Almost never block (heavy penalty)
4. **Feature engineering** - Agent must learn from rps + suspicious_pattern
5. **Reward shaping** - Health bonus encourages maintaining system stability

---

## 📊 Expected Performance

### Heuristic Baseline (block if rps > 30 OR suspicious)
- F1: ~0.60-0.70
- Precision: ~0.70-0.80
- Recall: ~0.50-0.65
- System Health: ~75-85%

### Goal for RL Agent
- F1: > 0.80
- Precision: > 0.85
- System Health: > 90%
- Minimize premium penalties

---

Good luck with your RL agent! 🚀
