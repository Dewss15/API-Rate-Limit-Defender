# 🧠 DQN Training Guide

## Overview

This guide explains how to train a Deep Q-Network (DQN) agent for the API Rate Limit Defender environment using curriculum learning.

---

## 📁 **Files Created**

1. **train_dqn.py** (20.8KB) - DQN training script with curriculum learning
2. **test_pt_model.py** (14.3KB) - Verification script for trained model
3. **DQN_TRAINING_GUIDE.md** (this file) - Complete usage guide

---

## 🎯 **Training Strategy**

### **Curriculum Learning (3 Phases)**

```
Phase 1: WARMUP (100 episodes)
└─ Dataset: Easy (10 users)
└─ Goal: Learn basic patterns (obvious bots)
└─ Expected F1: 0.95+

Phase 2: HARDENING (200 episodes)
└─ Dataset: Medium (20 users)
└─ Goal: Handle RPS overlap
└─ Expected F1: 0.80+

Phase 3: ADVERSARIAL (500 episodes)
└─ Dataset: Winning (83 users)
└─ Goal: Master edge cases
└─ Expected F1: 0.80+
```

### **Exploration Strategy**

- **Epsilon-Greedy:** Start at ε=1.0 (full random), decay to ε=0.01 (mostly greedy)
- **Decay Rate:** 0.995 per episode
- **Final Epsilon:** 0.01 (1% exploration at end)

### **Model Architecture**

```
Input Layer:  3 features per user
  ├─ Normalized RPS (0 to 1)
  ├─ Suspicious pattern flag (0 or 1)
  └─ Tier flag (1 if premium, else 0)

Hidden Layer 1: 64 units + ReLU
Hidden Layer 2: 64 units + ReLU

Output Layer: 2 Q-values
  ├─ Q(s, noop)
  └─ Q(s, block)
```

### **Hyperparameters**

| Parameter | Value | Description |
|-----------|-------|-------------|
| Learning Rate | 0.001 | Adam optimizer |
| Gamma (γ) | 0.95 | Discount factor |
| Batch Size | 64 | Replay buffer batch |
| Buffer Capacity | 10,000 | Experience replay size |
| Target Update | Every 10 episodes | Target network sync |
| Validation Freq | Every 50 episodes | Check on extreme data |

---

## 🚀 **Usage**

### **Step 1: Install Dependencies**

```bash
pip install torch numpy
```

### **Step 2: Train the Model**

```bash
cd "c:\Users\Dewpearl Gonsalves\meta"
python train_dqn.py
```

**Expected output:**
```
======================================================================
DQN Training for API Rate Limit Defender
======================================================================
Device: cpu
Network: DefenderNetwork(...)

======================================================================
PHASE 1: WARMUP (Easy Data)
======================================================================
Episode 20/100: F1=0.950, Score=0.923, Reward=1.50, Loss=0.0234, ε=0.818
Episode 40/100: F1=0.950, Score=0.923, Reward=1.50, Loss=0.0187, ε=0.669
  → Validation F1: 0.756
  → New best model saved! F1: 0.756
...

======================================================================
PHASE 2: HARDENING (Medium Data)
======================================================================
Episode 40/200: F1=0.812, Score=0.798, Reward=2.10, Loss=0.0145, ε=0.547
  → Validation F1: 0.782
  → New best model saved! F1: 0.782
...

======================================================================
PHASE 3: ADVERSARIAL (Winning Data)
======================================================================
Episode 100/500: F1=0.798, Score=0.776, Reward=3.45, Loss=0.0112, ε=0.367
  → Validation F1: 0.801
  → New best model saved! F1: 0.801
...

======================================================================
FINAL VALIDATION
======================================================================
Easy: F1=0.950, Precision=1.000, Recall=0.950, Score=0.923, Premium Penalty=0
Medium: F1=0.825, Precision=0.889, Recall=0.769, Score=0.812, Premium Penalty=0
Extreme: F1=0.801, Precision=0.856, Recall=0.752, Score=0.798, Premium Penalty=0
Winning: F1=0.798, Precision=0.842, Recall=0.758, Score=0.785, Premium Penalty=0

Best model saved to: best_model.pt
Best validation F1: 0.801

Training complete!
```

**Training time:** ~20-40 minutes (CPU), ~5-10 minutes (GPU)

---

### **Step 3: Verify the Model**

```bash
python test_pt_model.py
```

**Expected output:**
```
======================================================================
DQN Model Validation
======================================================================

Loading model from: best_model.pt
✅ Model loaded from best_model.pt

======================================================================
TEST 1: Meta-Strict Logging (Winning Dataset)
======================================================================

[START] task=adversarial-defense env=api-defender model=DQN-v1
[STEP] step=1 action=block(U15) reward=0.50 done=False error=null
[STEP] step=2 action=block(U18) reward=0.50 done=False error=null
...
[END] success=true steps=18 score=0.785 rewards=0.50,0.50,0.50,...

======================================================================
TEST 2: Performance Across All Datasets
======================================================================

Easy      : F1=0.950, Precision=1.000, Recall=0.950, Score=0.923, Premium=0
Medium    : F1=0.825, Precision=0.889, Recall=0.769, Score=0.812, Premium=0
Winning   : F1=0.798, Precision=0.842, Recall=0.758, Score=0.785, Premium=0

======================================================================
TEST 3: Premium Protection Validation
======================================================================

✅ PASS: Agent never blocked premium users

======================================================================
TEST 4: Logging Format Validation
======================================================================

✅ PASS: All logs use Meta-strict format
   - [START] format: task=<id> env=<name> model=<name>
   - [STEP] format: step=<n> action=<str> reward=<0.00> done=<bool> error=<msg>
   - [END] format: success=<bool> steps=<n> score=<0.000> rewards=<r1,r2,...>

======================================================================
VALIDATION SUMMARY
======================================================================

Model: best_model.pt
Device: cpu

Results:
  Winning F1:        0.798
  Winning Score:     0.785
  Premium Blocked:   0

Pass/Fail Criteria:
  ✅ Model loads:              True
  ✅ F1 > 0.70:              0.798
  ✅ No premium blocked:      True
  ✅ Logging format correct:  True

🎉 ALL TESTS PASSED! Model is ready for submission!
```

---

### **Step 4: Quick Test (Optional)**

For a faster validation:

```bash
python test_pt_model.py --quick
```

---

## 🔧 **Customization**

### **Adjust Training Duration**

Edit `train_dqn.py`, find the `main()` function:

```python
train_curriculum(
    agent,
    easy_episodes=100,      # ← Increase for more warmup
    medium_episodes=200,    # ← Increase for better medium performance
    winning_episodes=500,   # ← Increase for better winning performance
    target_update_freq=10,
    validation_freq=50,
    save_path="best_model.pt"
)
```

### **Adjust Hyperparameters**

Edit `train_dqn.py`, find the agent creation:

```python
agent = DQNAgent(
    input_dim=3,
    hidden_dim=64,          # ← Increase for more capacity (128, 256)
    learning_rate=0.001,    # ← Try 0.0005 or 0.0001 for stability
    gamma=0.95,             # ← Try 0.99 for more future focus
    epsilon_start=1.0,
    epsilon_end=0.01,       # ← Try 0.05 for more exploration
    epsilon_decay=0.995,    # ← Try 0.99 for slower decay
    buffer_capacity=10000,  # ← Increase for more memory
    batch_size=64           # ← Try 32 or 128
)
```

### **Use GPU**

The training script automatically detects and uses GPU if available:

```python
# Check if GPU is being used
print(f"Device: {agent.device}")  # Should print "cuda" if GPU available
```

To force CPU:
```python
agent = DQNAgent(..., device="cpu")
```

---

## 📊 **Expected Performance**

### **Target Metrics**

| Dataset | Target F1 | Typical F1 | Notes |
|---------|-----------|------------|-------|
| Easy | 0.95+ | 0.95-1.00 | Should be perfect |
| Medium | 0.80+ | 0.75-0.85 | Good overlap handling |
| Extreme | 0.75+ | 0.70-0.80 | Premium protection |
| Winning | 0.80+ | 0.75-0.85 | Final target |

### **Training Progress**

Typical learning curve:

```
Episodes 0-100 (Easy):
  └─ F1 quickly reaches 0.95+
  └─ Loss decreases from 1.0 to 0.02
  └─ Epsilon decays to ~0.60

Episodes 100-300 (Medium):
  └─ F1 starts at 0.70, improves to 0.80+
  └─ Loss stabilizes around 0.01
  └─ Epsilon decays to ~0.20

Episodes 300-800 (Winning):
  └─ F1 gradually improves from 0.70 to 0.80+
  └─ Loss remains stable at 0.01
  └─ Epsilon decays to 0.01 (final)
```

---

## 🐛 **Troubleshooting**

### **Issue 1: F1 score not improving**

**Symptoms:** F1 stays at 0.60-0.70 after 500+ episodes

**Solutions:**
- Increase training episodes (1000+)
- Lower learning rate (0.0005 or 0.0001)
- Increase hidden layer size (128 or 256)
- Check epsilon is decaying (should reach 0.01-0.1)

### **Issue 2: Agent blocks too many users (low precision)**

**Symptoms:** Precision < 0.70, lots of false positives

**Solutions:**
- The agent may be too aggressive
- Check reward balance (should be +0.4 bot, -0.5 human)
- Increase negative reward for blocking humans (-0.7)
- Add stronger premium penalty in feature extraction

### **Issue 3: Agent misses too many bots (low recall)**

**Symptoms:** Recall < 0.70, lots of false negatives

**Solutions:**
- The agent may be too conservative
- Increase positive reward for blocking bots (+0.5)
- Decrease negative reward for blocking humans (-0.3)
- Train longer on winning dataset

### **Issue 4: Agent blocks premium users**

**Symptoms:** premium_penalty > 0

**Solutions:**
- Check feature extraction (tier_flag should be 1 for premium)
- Add hard constraint in select_action (filter out premium before Q-value calculation)
- Add large negative reward (-5.0) for blocking premium during training

### **Issue 5: Loss increases during training**

**Symptoms:** Loss goes up instead of down

**Solutions:**
- Lower learning rate (0.0005 or 0.0001)
- Increase batch size (128 or 256)
- Add gradient clipping (already included, check value)
- Check for bugs in reward calculation

### **Issue 6: Model not saving**

**Symptoms:** "FileNotFoundError" or "PermissionError"

**Solutions:**
- Check write permissions in directory
- Use absolute path: `save_path="c:/path/to/best_model.pt"`
- Check disk space

---

## 🔬 **Advanced: Understanding the Training**

### **Experience Replay**

The agent stores experiences (state, action, reward, next_state) in a buffer and samples random batches for training. This:
- Breaks correlation between consecutive samples
- Improves sample efficiency
- Stabilizes training

**Buffer size:** 10,000 experiences  
**Batch size:** 64 samples per update

### **Target Network**

The agent uses two networks:
- **Policy Network:** Updated every step
- **Target Network:** Updated every 10 episodes

This prevents the "moving target" problem in Q-learning.

### **Epsilon-Greedy Exploration**

```python
if random.random() < epsilon:
    action = random_action()  # Explore
else:
    action = best_action()    # Exploit
```

Epsilon starts at 1.0 (100% random) and decays to 0.01 (1% random).

**Decay formula:** `epsilon = max(epsilon_end, epsilon * epsilon_decay)`

### **Q-Learning Update**

```python
Q(s, a) ← Q(s, a) + α × [r + γ × max Q(s', a') - Q(s, a)]
```

Where:
- α = learning rate (0.001)
- γ = discount factor (0.95)
- r = immediate reward
- max Q(s', a') = best future Q-value (from target network)

---

## 📈 **Monitoring Training**

### **Key Metrics to Watch**

1. **F1 Score:** Should increase over time
2. **Loss:** Should decrease and stabilize
3. **Epsilon:** Should decay from 1.0 to 0.01
4. **Validation F1:** Should improve on extreme dataset
5. **Premium Penalty:** Should always be 0

### **When to Stop Training**

Stop when:
- Validation F1 > 0.80 ✅
- Loss < 0.02 ✅
- F1 plateaus for 100+ episodes ✅
- Premium penalty = 0 ✅

### **When to Train More**

Continue if:
- F1 still increasing ⬆️
- Validation F1 < 0.75 ⬇️
- Loss still decreasing ⬇️

---

## 🚀 **Integration with main.py**

Once `best_model.pt` is trained, use it with `sakshi_agent_example.py`:

```python
from sakshi_agent_example import SakshiAgent

# Load trained DQN model
agent = SakshiAgent(model_path="best_model.pt", confidence_threshold=0.7)

# Run with main.py
from main import ExecutionEngine
engine = ExecutionEngine(agent)
results = engine.run_all_tasks()
engine.print_final_summary(results)
```

**Expected output:**
```
[START] task=easy-triage env=api-defender model=Sakshi-DQN-v1
...
[END] success=true steps=4 score=0.923 rewards=...

FINAL_SUMMARY
Easy:    F1=0.950
Medium:  F1=0.825
Winning: F1=0.798
```

---

## ✅ **Pre-Submission Checklist**

- [ ] Trained model saved to `best_model.pt`
- [ ] Validation F1 > 0.70 on all datasets
- [ ] Premium penalty = 0 on all datasets
- [ ] Test script passes all 4 tests
- [ ] Model integrates with `sakshi_agent_example.py`
- [ ] Meta-strict logging format verified
- [ ] Model file size < 10MB

---

## 📚 **File Structure**

```
meta/
├── train_dqn.py              # Training script (this creates best_model.pt)
├── test_pt_model.py           # Verification script
├── best_model.pt              # Trained model (output)
├── sakshi_agent_example.py    # Integration template
├── main.py                    # Production bridge
└── DQN_TRAINING_GUIDE.md      # This guide
```

---

## 🎓 **Learning Resources**

**DQN Papers:**
- [Playing Atari with Deep RL](https://arxiv.org/abs/1312.5602) (original DQN)
- [Human-level control through deep RL](https://www.nature.com/articles/nature14236)

**Key Concepts:**
- Experience Replay
- Target Networks
- Epsilon-Greedy Exploration
- Q-Learning
- Temporal Difference Learning

---

## 🎉 **Success Criteria**

Your DQN is ready for submission when:

✅ **Training complete** (800 episodes)  
✅ **best_model.pt exists** (~1-2 MB)  
✅ **Validation F1 > 0.75** on winning dataset  
✅ **Premium penalty = 0** (never blocks premium)  
✅ **All 4 tests pass** in test_pt_model.py  
✅ **Integrates with main.py** successfully  

---

**Happy Training!** 🚀🧠

For questions or issues, refer to:
- `AGENT_ACCURACY_GUIDE.md` - General improvement tips
- `INTEGRATION_CHECKLIST.md` - Integration steps
- `README_MAIN_BRIDGE.md` - main.py documentation
