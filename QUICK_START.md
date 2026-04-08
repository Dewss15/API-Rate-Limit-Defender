# 🎯 Quick Start Guide - Agent Integration

## 🚀 **60-Second Setup**

### **For Heuristic Agent (Testing)**
```bash
cd "c:\Users\Dewpearl Gonsalves\meta"
python main.py
```

### **For Your Trained Agent (Sakshi)**
```bash
# 1. Copy your model
cp your_trained_model.pt best_model.pt

# 2. Run example
python sakshi_agent_example.py
```

---

## 📁 **File Guide**

| File | Purpose | Who Uses It |
|------|---------|-------------|
| `main.py` | **Production bridge** - connects agent to environment | Everyone |
| `sakshi_agent_example.py` | **Agent template** - how to wrap your trained model | Sakshi |
| `INTEGRATION_CHECKLIST.md` | **Step-by-step guide** - integration walkthrough | Sakshi |
| `README_MAIN_BRIDGE.md` | **Documentation** - detailed API reference | Everyone |
| `AGENT_ACCURACY_GUIDE.md` | **Training tips** - how to improve F1 score | Sakshi |

---

## 🎓 **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                               │
│  (The Bridge - Don't modify reward formula or logging)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─ Task 1: easy-triage (10 users)
                              ├─ Task 2: behavioral-analysis (20 users)
                              └─ Task 3: adversarial-defense (83 users)
                              
                              ↓
                              
┌─────────────────────────────────────────────────────────────┐
│                   YOUR AGENT (Sakshi)                        │
│  - HeuristicAgent (baseline)                                │
│  - LLMAgent (OpenAI API)                                    │
│  - SakshiAgent (your trained model) ← CUSTOMIZE THIS        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
                              
┌─────────────────────────────────────────────────────────────┐
│               APIRateLimitDefenderEnv                        │
│  (Environment - Already tested and working)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
                              
┌─────────────────────────────────────────────────────────────┐
│                      Grader                                  │
│  (Matches evaluator.py exactly - Don't modify)              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 **Integration Flow**

```
1. Train your model
   ↓
2. Save to best_model.pt
   ↓
3. Copy sakshi_agent_example.py
   ↓
4. Customize _extract_features()  ← Match your training!
   ↓
5. Customize _predict()           ← Match your model output!
   ↓
6. Test: python sakshi_agent_example.py
   ↓
7. Verify:
   - F1 > 0.70 ✓
   - No premium blocked ✓
   - Logging format correct ✓
   ↓
8. Submit!
```

---

## ⚡ **Key Integration Points**

### **1. Feature Extraction** (CRITICAL)
```python
def _extract_features(self, user, observation):
    # MUST MATCH YOUR TRAINING EXACTLY
    features = [
        user["rps"] / 100.0,              # Same normalization?
        float(user["is_suspicious_pattern"]),
        float(user["tier"] == "premium"),
        observation["system_health"],
        # ... add all features you used in training
    ]
    return torch.tensor(features)
```

### **2. Model Output Interpretation**
```python
def _predict(self, features):
    output = self.model(features)
    
    # Option A: Binary classification [noop, block]
    if output.shape[-1] == 2:
        probs = torch.softmax(output, dim=-1)
        return probs[1].item()  # Block probability
    
    # Option B: Single output
    elif output.shape[-1] == 1:
        return torch.sigmoid(output).item()
    
    # Option C: Q-values
    else:
        return 1.0 if output[1] > output[0] else 0.0
```

### **3. Premium Protection** (MANDATORY)
```python
def select_action(self, observation):
    for user in users:
        # NEVER block premium - hard constraint
        if user["tier"] == "premium":
            continue  # ← CRITICAL LINE
        
        # Your blocking logic here
        ...
```

---

## 📊 **Expected Output**

```
======================================================================
API Rate Limit Defender - Agent Integration Bridge
======================================================================
Agent: Sakshi-DQN-v1
======================================================================

[START] task=easy-triage env=api-defender model=Sakshi-DQN-v1
[STEP] step=1 action=block(U8) reward=0.50 done=False error=null
[STEP] step=2 action=block(U9) reward=0.50 done=False error=null
[STEP] step=3 action=block(U10) reward=0.50 done=False error=null
[STEP] step=4 action=noop reward=0.00 done=True error=null
[END] success=true steps=4 score=0.923 rewards=0.50,0.50,0.50,0.00

... (behavioral-analysis and adversarial-defense tasks)

======================================================================
FINAL_SUMMARY
======================================================================

Task: Easy Triage (easy-triage)
  Success:        True
  Steps:          4
  Final Score:    0.923
  F1 Score:       0.950
  Precision:      1.000
  Recall:         0.950
  System Health:  100.0%
  TP/FP/FN/TN:    3/0/0/7
  Premium Blocked: 0     ← MUST BE 0!
  Total Reward:   1.50

======================================================================
AGGREGATE METRICS
======================================================================
Average Score:         0.811
Average Precision:     0.913
Average System Health: 94.7%
Total Premium Blocked: 0      ← MUST BE 0!

======================================================================
VALIDATION
======================================================================
✅ No premium blocked:     True
✅ Avg F1 > 0.70:          True
✅ Avg health > 80%:       True
✅ All tasks completed:    True
```

---

## ⚠️ **Common Mistakes**

| ❌ Mistake | ✅ Solution |
|-----------|-----------|
| Model path wrong | Use absolute path or verify with `os.path.exists()` |
| Features don't match training | Document exact features during training |
| Block premium users | Add `if user["tier"] == "premium": continue` |
| Confidence too high (0.99) | Lower to 0.6-0.8 for better recall |
| Confidence too low (0.1) | Raise to 0.6-0.8 for better precision |
| Logging format wrong | Don't modify `ExecutionEngine.run_task()` |
| Forget to normalize RPS | Use `rps / 100.0` like in training |

---

## 🎯 **Success Metrics**

| Task | Minimum F1 | Target F1 | Your F1 |
|------|-----------|-----------|---------|
| Easy | 0.90 | 0.95+ | _____ |
| Medium | 0.70 | 0.80+ | _____ |
| Hard | 0.65 | 0.80+ | _____ |

**CRITICAL:** Premium blocked MUST be 0 on all tasks!

---

## 🚦 **3-Step Test**

### **Step 1: Test Feature Extraction**
```python
from sakshi_agent_example import test_feature_extraction
test_feature_extraction()
```
✅ Should print feature shape and values

### **Step 2: Test Single Task**
```python
from sakshi_agent_example import test_on_single_task
test_on_single_task()
```
✅ Should get F1 > 0.90 on easy data

### **Step 3: Test Full Integration**
```bash
python sakshi_agent_example.py
```
✅ Should complete all 3 tasks successfully

---

## 📞 **Quick Troubleshooting**

**Q: Model won't load**  
A: Check PyTorch version: `pip show torch`

**Q: Features dimension mismatch**  
A: Count features in `_extract_features()`, must match model input_dim

**Q: F1 too low**  
A: Adjust confidence_threshold (try 0.5, 0.6, 0.7, 0.8)

**Q: Agent blocks premium**  
A: Check `select_action()` has `if user["tier"] == "premium": continue`

**Q: All actions are noop**  
A: Lower confidence_threshold or check model predictions

---

## 🎓 **Learning Path**

1. **Start with baseline:** Run `python main.py` with HeuristicAgent
2. **Understand output:** Read the logs and final summary
3. **Test your model:** Run `test_feature_extraction()` and `test_on_single_task()`
4. **Integrate:** Customize `sakshi_agent_example.py`
5. **Tune:** Adjust confidence_threshold for best F1
6. **Validate:** Run full integration and check all metrics
7. **Submit:** Package everything and submit

---

## ✅ **Final Pre-Submission Check**

- [ ] Model file exists and loads
- [ ] Features match training exactly
- [ ] Premium protection verified
- [ ] F1 > 0.70 on all tasks
- [ ] No crashes or errors
- [ ] Logging format matches exactly
- [ ] Total premium blocked = 0
- [ ] Code is clean and commented

---

## 🎉 **Ready to Submit?**

If all checks pass, you're ready! 🚀

**Next Steps:**
1. Package all files
2. Test on clean environment
3. Submit to Meta OpenEnv
4. Celebrate! 🎊

---

**Good luck, Sakshi!** You've got this! 💪
