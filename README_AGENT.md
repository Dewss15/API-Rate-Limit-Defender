# 🤖 Agent Developer Guide - API Rate Limit Defender

> **For:** Sakshi (RL Agent Developer)  
> **Project:** API Rate Limit Defender  
> **Environment:** OpenEnv-compatible RL Environment  
> **Difficulty:** 🔴 Hard (requires inference from partial observations)

---

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Environment Overview](#environment-overview)
3. [Observation Schema (The Input)](#observation-schema)
4. [Action Schema (The Output)](#action-schema)
5. [Reward Structure](#reward-structure)
6. [Integration Guide](#integration-guide)
7. [Baseline Agent](#baseline-agent)
8. [Success Metrics](#success-metrics)
9. [Training Tips](#training-tips)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

```python
from environment import make_env
from data import get_winning_data

# Initialize environment
env = make_env()
data = get_winning_data()

# Start episode
obs = env.reset(data)

# Your agent loop
done = False
while not done:
    action = your_agent.select_action(obs)
    obs, reward, done, info = env.step(action)
    
# Evaluate
from evaluator import evaluate
results = evaluate(info["blocked_ids"], data)
print(f"F1 Score: {results['f1']:.4f}")
```

---

## 🎯 Environment Overview

### Mission
**Identify and block malicious bots while protecting legitimate users**, especially premium customers.

### Challenge
You must infer whether users are bots **without direct access** to the `is_bot` field. You only have:
- `rps` (requests per second)
- `is_suspicious_pattern` (behavioral flag)
- `tier` (normal vs premium)

### Constraints
- ⏱️ **Max 20 steps per episode**
- 💀 **Episode ends if `system_health` drops to 0**
- ⚠️ **Blocking premium users is extremely costly**

### The Tradeoff
- Block too aggressively → High False Positives → Lost legitimate users
- Block too conservatively → High False Negatives → System gets overwhelmed by bots

---

## 👁️ Observation Schema (The Input)

Your agent receives a dictionary from `env.step()` with the following structure:

```python
observation = {
    "users": [
        {
            "id": "U1",                      # Unique user identifier
            "rps": 45,                       # Requests per second
            "is_suspicious_pattern": True,   # Behavioral anomaly flag
            "tier": "normal"                 # "normal" or "premium"
        },
        # ... more users
    ],
    "blocked_users": ["U8", "U15"],         # Already blocked IDs
    "system_health": 0.85                    # Current health (0.0 to 1.0)
}
```

### 🔒 CRITICAL: Hidden Information

**⚠️ WARNING:** The `is_bot` field is **NOT** included in observations!

```python
# ❌ YOU CANNOT DO THIS
if user["is_bot"]:  # This will cause KeyError!
    block(user["id"])

# ✅ YOU MUST INFER FROM AVAILABLE SIGNALS
if user["rps"] > 50 and user["is_suspicious_pattern"]:
    block(user["id"])
```

The environment stores the ground truth `is_bot` for evaluation, but your agent must learn to predict it from the available features.

### Field Descriptions

| Field | Type | Description | Agent Strategy |
|-------|------|-------------|----------------|
| `id` | str | User identifier | Use to specify blocking action |
| `rps` | int | Requests/second | High RPS (>50) often indicates bots |
| `is_suspicious_pattern` | bool | Behavioral flag | Strong signal but not definitive |
| `tier` | str | User tier | **NEVER block "premium"** (huge penalty) |
| `blocked_users` | list | Already blocked | Avoid re-blocking (penalty: -0.1) |
| `system_health` | float | System status | <0.8 = bad, aim for >0.9 |

---

## ⚡ Action Schema (The Output)

Your agent must return a dictionary in this exact format:

```python
action = {
    "type": "block",
    "user_id": "U42"
}
```

### Action Rules
1. ✅ **Valid action:** Block an unblocked user that exists
2. ❌ **Invalid action:** 
   - Non-existent user ID → Penalty: **-0.1**
   - Already blocked user → Penalty: **-0.1**
   - Invalid action type → Penalty: **-0.1**

### How to Choose `user_id`

```python
def select_action(self, observation):
    for user in observation["users"]:
        # Skip already blocked users
        if user["id"] in observation["blocked_users"]:
            continue
        
        # Your decision logic here
        if self.should_block(user):
            return {"type": "block", "user_id": user["id"]}
    
    # No action needed (will incur -0.1 penalty but episode continues)
    return {"type": "block", "user_id": "no_action"}
```

---

## 💰 Reward Structure

### Per-Step Rewards

| Action | Reward | Notes |
|--------|--------|-------|
| Block a bot | **+0.4** | Correct detection |
| Block a human (normal) | **-0.5** | False positive |
| Block a human (premium) | **-0.5** | Same reward, but tracked separately |
| Health > 0.8 (bonus) | **+0.1** | Only for valid actions |
| Invalid action | **-0.1** | Wrong user ID, already blocked, etc. |

### Important Notes

1. **Premium Penalty:** Blocking premium users gives the same -0.5 reward, but:
   - Tracked in `info["premium_penalty"]`
   - Heavily penalized in the final evaluator score
   - Your agent should **almost never** block premium users

2. **Health Bonus:** You get +0.1 extra if `system_health > 0.8` **and** you make a valid block action

3. **Cumulative Reward:** Your total episode reward is the sum of all step rewards

### System Health Formula

```python
system_health = max(0, 1 - ((FN + FP) / total_users))
```

Where:
- **FN** = False Negatives (bots you missed)
- **FP** = False Positives (humans you blocked)

---

## 🔌 Integration Guide

### Step 1: Environment Setup

```python
from environment import make_env
from data import get_easy_data, get_medium_data, get_winning_data

# Create environment
env = make_env()

# Load dataset (start with easy)
data = get_easy_data()  # 10 users, obvious patterns
# data = get_medium_data()  # 20 users, some overlap
# data = get_winning_data()  # 83 users, realistic difficulty

# Reset environment
initial_obs = env.reset(data)
```

### Step 2: Create Your Agent Class

```python
class DefenderAgent:
    """Your RL Agent for blocking bots."""
    
    def __init__(self):
        # Initialize your model/policy here
        pass
    
    def select_action(self, observation):
        """
        Select which user to block based on observation.
        
        Args:
            observation: Dict with users, blocked_users, system_health
            
        Returns:
            action: Dict with {"type": "block", "user_id": str}
        """
        # TODO: Implement your policy
        pass
    
    def update(self, obs, action, reward, next_obs, done):
        """
        Update your agent based on experience.
        
        Args:
            obs: Previous observation
            action: Action taken
            reward: Reward received
            next_obs: New observation
            done: Episode termination flag
        """
        # TODO: Implement learning update (Q-learning, DQN, PPO, etc.)
        pass
```

### Step 3: Training Loop

```python
# Training parameters
num_episodes = 1000
data = get_winning_data()

agent = DefenderAgent()

for episode in range(num_episodes):
    obs = env.reset(data)
    done = False
    episode_reward = 0
    
    while not done:
        # Agent selects action
        action = agent.select_action(obs)
        
        # Environment steps
        next_obs, reward, done, info = env.step(action)
        
        # Agent learns
        agent.update(obs, action, reward, next_obs, done)
        
        episode_reward += reward
        obs = next_obs
    
    # Log progress
    if episode % 100 == 0:
        print(f"Episode {episode}: Reward={episode_reward:.2f}, "
              f"TP={info['tp']}, FP={info['fp']}, FN={info['fn']}")
```

### Step 4: Evaluation

```python
from evaluator import evaluate

# Run final evaluation
obs = env.reset(data)
done = False

while not done:
    action = agent.select_action(obs)
    obs, reward, done, info = env.step(action)

# Get official score
results = evaluate(info["blocked_ids"], data)

print("\n=== FINAL RESULTS ===")
print(f"Score:         {results['score']:.4f}")
print(f"F1:            {results['f1']:.4f}")
print(f"Precision:     {results['precision']:.4f}")
print(f"Recall:        {results['recall']:.4f}")
print(f"System Health: {results['system_health']:.2%}")
```

---

## 🎓 Baseline Agent

Here's a simple heuristic baseline to get you started:

```python
class HeuristicAgent:
    """Baseline heuristic agent."""
    
    def __init__(self, rps_threshold=40):
        self.rps_threshold = rps_threshold
    
    def select_action(self, observation):
        """Block users with high RPS AND suspicious patterns."""
        
        for user in observation["users"]:
            # Skip already blocked
            if user["id"] in observation["blocked_users"]:
                continue
            
            # NEVER block premium users
            if user["tier"] == "premium":
                continue
            
            # Block if both conditions met
            if user["rps"] > self.rps_threshold and user["is_suspicious_pattern"]:
                return {"type": "block", "user_id": user["id"]}
        
        # No valid action found
        return {"type": "block", "user_id": "no_action"}
```

### Baseline Performance
- F1 Score: ~0.65-0.70
- Precision: ~0.75-0.80
- Recall: ~0.55-0.65
- System Health: ~80-85%

**Your goal:** Beat this baseline with machine learning!

---

## 🎯 Success Metrics

### Target Performance

| Metric | Target | Minimum |
|--------|--------|---------|
| **F1 Score** | **> 0.80** | > 0.75 |
| **Precision** | > 0.85 | > 0.80 |
| **Recall** | > 0.80 | > 0.70 |
| **System Health** | **> 90%** | > 85% |
| **Premium Penalties** | **0** | < 2 |

### Evaluation Breakdown

The final score is calculated by the evaluator:

```python
score = (0.6 * f1) + (0.3 * system_health) - (0.1 * premium_penalty_rate)
```

**Key Insights:**
1. F1 is most important (60% weight)
2. System health is critical (30% weight)
3. Premium penalties are devastating (10% weight)

---

## 💡 Training Tips

### Feature Engineering Ideas

Since you can't see `is_bot`, engineer features from what you have:

```python
def extract_features(user, observation):
    features = {
        "rps": user["rps"],
        "is_suspicious": int(user["is_suspicious_pattern"]),
        "is_premium": int(user["tier"] == "premium"),
        "rps_normalized": user["rps"] / 100.0,  # Normalize
        
        # Composite features
        "suspicious_high_rps": int(
            user["is_suspicious_pattern"] and user["rps"] > 50
        ),
        "safe_premium": int(
            user["tier"] == "premium" and not user["is_suspicious_pattern"]
        ),
        
        # Context features
        "current_health": observation["system_health"],
        "num_blocked": len(observation["blocked_users"]),
    }
    return features
```

### Algorithm Suggestions

1. **Q-Learning / DQN**
   - State: Feature vector of user + context
   - Action: Block or skip
   - Good starting point

2. **Policy Gradient (PPO)**
   - Better for continuous decision-making
   - Can learn complex policies

3. **Imitation Learning**
   - Train on expert demonstrations (heuristic agent)
   - Then fine-tune with RL

### Hyperparameter Tuning

```python
# Learning rate
learning_rate = 0.001

# Exploration
epsilon_start = 1.0
epsilon_end = 0.01
epsilon_decay = 0.995

# Discount factor
gamma = 0.95  # Future rewards matter

# Experience replay
buffer_size = 10000
batch_size = 64
```

### Progressive Training

```python
# Stage 1: Easy data (build confidence)
train_on(get_easy_data(), episodes=500)

# Stage 2: Medium data (handle ambiguity)
train_on(get_medium_data(), episodes=1000)

# Stage 3: Winning data (realistic challenge)
train_on(get_winning_data(), episodes=2000)
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. KeyError: 'is_bot'
```python
# ❌ WRONG
if user["is_bot"]:
    block(user)

# ✅ CORRECT
if user["rps"] > threshold and user["is_suspicious_pattern"]:
    block(user)
```

#### 2. Blocking Premium Users
```python
# Always add this check FIRST
if user["tier"] == "premium":
    continue  # Skip premium users
```

#### 3. Reward is 0.0 for Valid Actions
- Check if you're blocking already-blocked users
- This gives -0.1 + 0.1 (health bonus) = 0.0

#### 4. Episode Ends Too Early
- System health dropped to 0
- Too many False Positives or False Negatives
- Be more conservative initially

#### 5. Low Recall (Missing Bots)
- Your threshold is too high
- Not all bots have high RPS (stealth bots exist!)
- Look at `is_suspicious_pattern` more carefully

#### 6. Low Precision (Blocking Humans)
- Your threshold is too low
- Some humans have suspicious patterns
- Consider combining multiple signals

---

## 📚 Additional Resources

### Files You Need
- `environment.py` - RL environment (already created)
- `models.py` - Data models (already created)
- `data.py` - Datasets (provided by team)
- `evaluator.py` - Scoring function (provided by team)

### Testing Your Agent
```bash
# Run tests
python test_environment.py

# Run examples
python example_usage.py

# Test your agent
python your_agent.py
```

### Example Agent Template

See `example_usage.py` for complete working examples.

---

## 🚦 Development Workflow

1. **Start Simple**
   - Implement heuristic baseline
   - Verify it works with `get_easy_data()`
   - Aim for F1 > 0.65

2. **Add Learning**
   - Implement Q-learning or DQN
   - Train on `get_medium_data()`
   - Aim for F1 > 0.75

3. **Optimize**
   - Fine-tune hyperparameters
   - Add feature engineering
   - Train on `get_winning_data()`
   - Aim for F1 > 0.80

4. **Validate**
   - Run multiple episodes
   - Check premium penalty count
   - Ensure system health > 90%

---

## ✅ Checklist

Before submitting your agent:

- [ ] Agent does NOT access `is_bot` field
- [ ] Premium users are rarely/never blocked (< 2 penalties)
- [ ] F1 Score > 0.80 on `get_winning_data()`
- [ ] System Health > 90%
- [ ] Agent completes episodes without crashing
- [ ] Code is well-documented
- [ ] Results are reproducible (set random seeds)

---

## 🎓 Good Luck!

Remember:
- 🎯 **Inference is key** - You must learn to predict bots from partial data
- 💎 **Premium users are sacred** - Almost never block them
- ⚖️ **Balance precision and recall** - Both matter for F1
- 🏥 **System health is critical** - Keep FP + FN low
- 🔬 **Experiment and iterate** - Try different approaches

**You've got this, Sakshi! 🚀**

---

Questions? Check:
1. `README_TESTING.md` - How to test the environment
2. `example_usage.py` - Working agent examples
3. `test_environment.py` - Environment validation

**Contact:** Check with Dewpearl (Environment) or Anchal (Evaluator) for technical questions.
