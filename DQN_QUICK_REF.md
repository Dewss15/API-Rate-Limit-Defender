# 🧠 DQN Quick Reference Card

**One-page guide for training and testing your DQN model**

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Train the model (20-40 min)
python train_dqn.py

# 2. Verify the model (30 sec)
python test_pt_model.py

# 3. Use in production (instant)
python main.py
```

---

## 📁 Key Files

| File | Purpose | Size |
|------|---------|------|
| `train_dqn.py` | Train DQN model | 20.8KB |
| `test_pt_model.py` | Verify trained model | 14.3KB |
| `best_model.pt` | Trained model (output) | ~1-2MB |
| `sakshi_agent_example.py` | Integration template | 12.2KB |
| `main.py` | Production bridge | 19.7KB |

---

## 🎯 Training Strategy

### Architecture
```
Input → 64 → 64 → Output
  3      ReLU  ReLU    2
```

### Curriculum Learning
```
Easy (100 eps) → Medium (200 eps) → Winning (500 eps)
  F1: 0.95         F1: 0.80           F1: 0.80
```

### Hyperparameters
- **Learning Rate:** 0.001
- **Epsilon:** 1.0 → 0.01 (decay 0.995)
- **Batch Size:** 64
- **Buffer:** 10,000 experiences
- **Target Update:** Every 10 episodes

---

## 📊 Expected Performance

| Dataset | F1 Target | Typical Range |
|---------|-----------|---------------|
| Easy | 0.95+ | 0.95-1.00 |
| Medium | 0.80+ | 0.75-0.85 |
| Extreme | 0.75+ | 0.70-0.80 |
| Winning | 0.80+ | 0.75-0.85 |

---

## ✅ Validation Checklist

**After Training:**
- [ ] best_model.pt exists (~1-2 MB)
- [ ] Validation F1 > 0.75
- [ ] Training log shows decreasing loss

**Run Verification:**
```bash
python test_pt_model.py
```

- [ ] Test 1: Meta-strict logging ✅
- [ ] Test 2: All datasets F1 > 0.70 ✅
- [ ] Test 3: Premium penalty = 0 ✅
- [ ] Test 4: Logging format correct ✅

**Integration Test:**
```bash
python main.py
```

- [ ] All 3 tasks complete
- [ ] F1 scores match test_pt_model.py
- [ ] No crashes or errors

---

## 🐛 Troubleshooting

### F1 Too Low (< 0.70)
```python
# In train_dqn.py, increase:
winning_episodes=1000  # was 500
hidden_dim=128         # was 64
```

### Agent Too Aggressive (Low Precision)
```python
# In environment.py, increase human penalty:
reward = -0.7  # was -0.5 (for blocking human)
```

### Agent Too Conservative (Low Recall)
```python
# In environment.py, increase bot reward:
reward = 0.5  # was 0.4 (for blocking bot)
```

### Blocks Premium Users
```python
# In train_dqn.py select_action(), add filter:
available_users = [
    u for u in users 
    if u["tier"] != "premium"  # ← Add this
]
```

### Loss Exploding
```python
# In train_dqn.py, lower learning rate:
learning_rate=0.0005  # was 0.001
```

---

## 🔧 Common Customizations

### Train Longer
```python
# train_dqn.py line ~540
train_curriculum(
    agent,
    easy_episodes=100,
    medium_episodes=200,
    winning_episodes=1000,  # ← Change from 500
)
```

### Use GPU
```python
# Automatic - checks torch.cuda.is_available()
# Force CPU: device="cpu" in agent creation
```

### Adjust Exploration
```python
# train_dqn.py line ~480
agent = DQNAgent(
    epsilon_start=1.0,
    epsilon_end=0.05,      # ← Change from 0.01
    epsilon_decay=0.99,    # ← Change from 0.995
)
```

### Bigger Network
```python
# train_dqn.py line ~475
agent = DQNAgent(
    hidden_dim=128,  # ← Change from 64
)
```

---

## 📈 Training Progress Indicators

### Healthy Training
```
Episode 100: F1=0.95, Loss=0.02, ε=0.60  ✅
Episode 300: F1=0.82, Loss=0.01, ε=0.20  ✅
Episode 800: F1=0.80, Loss=0.01, ε=0.01  ✅
```

### Unhealthy Training
```
Episode 100: F1=0.50, Loss=1.50, ε=0.60  ❌ (not learning)
Episode 300: F1=0.82, Loss=0.50, ε=0.20  ❌ (loss too high)
Episode 800: F1=0.60, Loss=0.01, ε=0.01  ❌ (F1 too low)
```

---

## 🎯 Success Criteria

**Training:**
- ✅ Completed 800 episodes
- ✅ best_model.pt saved
- ✅ Validation F1 > 0.75
- ✅ Loss < 0.02

**Verification:**
- ✅ All 4 tests pass
- ✅ Winning F1 > 0.70
- ✅ Premium penalty = 0

**Integration:**
- ✅ Works with main.py
- ✅ Produces correct logs
- ✅ All tasks complete

---

## 💡 Quick Tips

1. **Start with default settings** - they work well
2. **Watch validation F1** - more important than training F1
3. **Premium penalty must be 0** - non-negotiable
4. **Loss should decrease** - if not, lower learning rate
5. **Epsilon should decay** - check training logs
6. **GPU speeds up training** - 3-4x faster
7. **Patience pays off** - 800 episodes is necessary
8. **Test before celebrating** - run test_pt_model.py

---

## 📞 Help Resources

| Issue | Resource |
|-------|----------|
| General improvement | AGENT_ACCURACY_GUIDE.md |
| Integration help | INTEGRATION_CHECKLIST.md |
| Main.py usage | README_MAIN_BRIDGE.md |
| Detailed training | DQN_TRAINING_GUIDE.md |
| File overview | FILE_ANALYSIS.md |

---

## 🎉 Final Flow

```
train_dqn.py  →  best_model.pt  →  test_pt_model.py  →  main.py
   (30 min)        (output)           (30 sec)          (instant)
```

**That's it!** 🚀

---

**Pro Tip:** If training takes too long, reduce episodes to 50/100/300 for quick testing, then run full 100/200/500 for final model.
