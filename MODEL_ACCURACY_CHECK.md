# ✅ Model Accuracy Verification Guide

## How to Check if Your DQN Model is Accurate

---

## 🎯 Quick Answer

Run this command after training:

```bash
python test_pt_model.py
```

**Expected result if model is good:**
```
🎉 ALL TESTS PASSED! Model is ready for submission!
```

---

## 📊 Step-by-Step Verification

### **Step 1: Run Comprehensive Tests**

After training completes and you have `best_model.pt`, run:

```bash
python test_pt_model.py
```

This runs 4 critical tests automatically.

---

### **Step 2: Interpret Test Results**

#### ✅ **Test 1: Meta-Strict Logging**

**What it checks:** Output format is correct for submission

**Expected output:**
```
======================================================================
TEST 1: Meta-Strict Logging (Winning Dataset)
======================================================================

[START] task=adversarial-defense env=api-defender model=DQN-v1
[STEP] step=1 action=block(U15) reward=0.50 done=False error=null
[STEP] step=2 action=block(U18) reward=0.50 done=False error=null
...
[END] success=true steps=18 score=0.785 rewards=0.50,0.50,...
```

**Pass criteria:** ✅ Logs appear in correct format

---

#### ✅ **Test 2: Performance Across Datasets**

**What it checks:** Model works on all difficulty levels

**Expected output:**
```
======================================================================
TEST 2: Performance Across All Datasets
======================================================================

Easy      : F1=0.950, Precision=1.000, Recall=0.950, Score=0.923, Premium=0
Medium    : F1=0.825, Precision=0.889, Recall=0.769, Score=0.812, Premium=0
Winning   : F1=0.798, Precision=0.842, Recall=0.758, Score=0.785, Premium=0
```

**Pass criteria:**
- ✅ Easy F1 > 0.90 (should be nearly perfect)
- ✅ Medium F1 > 0.75 (good overlap handling)
- ✅ Winning F1 > 0.70 (target for deployment)
- ✅ All Premium = 0 (never blocks premium users)

---

#### ✅ **Test 3: Premium Protection**

**What it checks:** Model NEVER blocks premium users (critical!)

**Expected output:**
```
======================================================================
TEST 3: Premium Protection Validation
======================================================================

✅ PASS: Agent never blocked premium users
```

**Pass criteria:** ✅ No premium users blocked

**If FAIL:**
```
❌ FAIL: Agent blocked premium users: ['P1', 'P2']
```
→ Model is **BROKEN**, do not use! Retrain required.

---

#### ✅ **Test 4: Logging Format**

**What it checks:** All logs match expected structure

**Expected output:**
```
======================================================================
TEST 4: Logging Format Validation
======================================================================

✅ PASS: All logs use Meta-strict format
   - [START] format: task=<id> env=<name> model=<name>
   - [STEP] format: step=<n> action=<str> reward=<0.00> done=<bool> error=<msg>
   - [END] format: success=<bool> steps=<n> score=<0.000> rewards=<r1,r2,...>
```

**Pass criteria:** ✅ All format checks pass

---

### **Step 3: Check Final Summary**

**Expected output:**
```
======================================================================
VALIDATION SUMMARY
======================================================================

Model: best_model.pt
Device: cuda

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

## 📈 Understanding Metrics

### **F1 Score (Most Important)**

**What it is:** Balance between precision and recall

**Formula:** `F1 = 2 × (Precision × Recall) / (Precision + Recall)`

**Interpretation:**

| F1 Score | Quality | Meaning |
|----------|---------|---------|
| 0.90-1.00 | 🌟 Excellent | Nearly perfect bot detection |
| 0.80-0.89 | ✅ Good | Production-ready |
| 0.70-0.79 | ⚠️ Acceptable | Borderline, may need improvement |
| 0.60-0.69 | ❌ Poor | Not ready, retrain needed |
| < 0.60 | ❌ Bad | Broken, retrain required |

**Your target:** F1 > 0.70 on winning dataset

---

### **Precision**

**What it is:** Of all users you blocked, how many were actually bots?

**Formula:** `Precision = TP / (TP + FP)`

**Interpretation:**

| Precision | Meaning |
|-----------|---------|
| 1.00 | Perfect - never blocked a human |
| 0.90 | Excellent - 9 out of 10 blocks are correct |
| 0.80 | Good - 8 out of 10 blocks are correct |
| < 0.70 | Too aggressive - blocking too many humans |

**High precision, low recall:** Too conservative (missing bots)

---

### **Recall**

**What it is:** Of all bots in the dataset, how many did you catch?

**Formula:** `Recall = TP / (TP + FN)`

**Interpretation:**

| Recall | Meaning |
|--------|---------|
| 1.00 | Perfect - caught all bots |
| 0.90 | Excellent - caught 9 out of 10 bots |
| 0.80 | Good - caught 8 out of 10 bots |
| < 0.70 | Too conservative - missing too many bots |

**Low precision, high recall:** Too aggressive (blocking many humans)

---

### **Score (Final Grade)**

**Formula (from evaluator.py):**
```
score = (0.6 × F1) + (0.3 × system_health) - (0.1 × premium_penalty_rate)
```

**Interpretation:**

| Score | Grade | Submission? |
|-------|-------|-------------|
| 0.85-1.00 | A+ | Excellent submission |
| 0.75-0.84 | A | Good submission |
| 0.70-0.74 | B | Acceptable submission |
| 0.60-0.69 | C | Needs improvement |
| < 0.60 | F | Do not submit |

**Your target:** Score > 0.70

---

### **Premium Penalty (Critical)**

**What it is:** Number of premium users blocked

**Acceptable value:** **MUST be 0**

**If > 0:**
- ❌ Model is BROKEN
- ❌ Will fail submission
- ❌ Retrain immediately

**Why it matters:**
- Blocking 1 premium = -1.5 reward
- Equivalent to missing ~11 bots
- Hard constraint in competition

---

## 🔍 Detailed Accuracy Check

### **Method 1: Using test_pt_model.py (Recommended)**

```bash
python test_pt_model.py
```

**Pros:**
- Runs all 4 tests automatically
- Shows detailed metrics
- Validates logging format
- Checks premium protection

**Time:** ~30 seconds

---

### **Method 2: Quick Test**

```bash
python test_pt_model.py --quick
```

**Output:**
```
Quick Test: Loading and testing model...

✅ Model loaded from best_model.pt
Running episode on easy data...
  Step 1: block(U01) -> reward=0.50
  Step 2: block(U02) -> reward=0.50
  Step 3: block(U03) -> reward=0.50
  Step 4: block(U04) -> reward=0.50
  Step 5: noop(None) -> reward=0.10

Results: F1=0.950, Score=0.923

✅ Quick test passed!
```

**Time:** ~5 seconds

---

### **Method 3: Manual Validation**

Create a test script:

```python
import torch
from test_pt_model import TrainedDQNAgent
from environment import APIRateLimitDefenderEnv
from data import get_winning_data
from grader import Grader

# Load model
agent = TrainedDQNAgent("best_model.pt")
print(f"Device: {agent.device}")

# Test on winning data
env = APIRateLimitDefenderEnv()
dataset = get_winning_data()
obs = env.reset(dataset)

done = False
step = 0
while not done and step < 20:
    step += 1
    action = agent.select_action(obs)
    obs, reward, done, info = env.step(action)
    print(f"Step {step}: {action['type']}({action.get('user_id', 'None')}) -> reward={reward:.2f}")

# Grade
grader = Grader()
results = grader.grade(info["blocked_ids"], dataset)

print(f"\nResults:")
print(f"  F1:        {results['f1']:.3f}")
print(f"  Precision: {results['precision']:.3f}")
print(f"  Recall:    {results['recall']:.3f}")
print(f"  Score:     {results['score']:.3f}")
print(f"  Premium:   {results['premium_penalty']}")

# Pass/Fail
if results['f1'] > 0.70 and results['premium_penalty'] == 0:
    print("\n✅ Model is accurate!")
else:
    print("\n❌ Model needs improvement")
```

---

## 🎯 Accuracy Benchmarks

### **Comparison with Baselines**

| Agent Type | Easy F1 | Medium F1 | Winning F1 | Premium |
|------------|---------|-----------|------------|---------|
| Conservative | 1.00 | 0.60 | 0.60 | 0 |
| Smart | 0.95 | 0.75 | 0.75 | 0 |
| **DQN (Target)** | **0.95+** | **0.80+** | **0.80+** | **0** |

**Your model should beat the Smart baseline!**

---

### **Dataset-Specific Targets**

| Dataset | Users | Target F1 | Why |
|---------|-------|-----------|-----|
| Easy | 10 | 0.95+ | Obvious bots, should be perfect |
| Medium | 20 | 0.80+ | Some overlap, needs smart decisions |
| Extreme | 40 | 0.75+ | Premium traps, tests protection |
| Winning | 83 | 0.80+ | Final test, production-ready |

---

## ❌ Common Accuracy Issues

### **Issue 1: Low F1 on Winning Dataset (< 0.70)**

**Symptoms:**
```
Winning   : F1=0.650, Precision=0.700, Recall=0.600, Score=0.640, Premium=0
```

**Diagnosis:** Model undertrained or poor features

**Fix:**
1. Train longer (1000+ episodes on winning data)
2. Increase hidden layer size (128 instead of 64)
3. Lower learning rate (0.0005 instead of 0.001)

---

### **Issue 2: Premium Users Blocked**

**Symptoms:**
```
❌ FAIL: Agent blocked premium users: ['P1', 'P2']
Winning   : F1=0.800, Premium=2
```

**Diagnosis:** CRITICAL BUG - model ignoring tier

**Fix:**
1. Check `sakshi_agent_example.py` - must filter premium BEFORE Q-value calculation
2. Retrain with stronger premium penalty (-3.0 instead of -1.5)
3. Add hard constraint in feature extraction

**Code fix:**
```python
# In select_action(), add this filter:
available_users = [
    u for u in users
    if u["id"] not in blocked_users and u["tier"] != "premium"  # ← Critical
]
```

---

### **Issue 3: High Precision, Low Recall**

**Symptoms:**
```
Winning   : F1=0.700, Precision=0.950, Recall=0.550, Score=0.700, Premium=0
```

**Diagnosis:** Model too conservative (missing bots)

**Fix:**
1. Increase reward for blocking bots (+0.5 instead of +0.4)
2. Decrease penalty for blocking humans (-0.3 instead of -0.5)
3. Train more on easy data (better recall learning)

---

### **Issue 4: Low Precision, High Recall**

**Symptoms:**
```
Winning   : F1=0.720, Precision=0.600, Recall=0.900, Score=0.650, Premium=0
```

**Diagnosis:** Model too aggressive (blocking humans)

**Fix:**
1. Increase penalty for blocking humans (-0.7 instead of -0.5)
2. Train more on medium data (better precision learning)
3. Lower epsilon_end (0.05 instead of 0.01 for more exploration)

---

### **Issue 5: Inconsistent Results**

**Symptoms:** F1 varies widely between runs

**Diagnosis:** Model not converged or randomness in code

**Fix:**
1. Train longer (ensure loss < 0.02)
2. Check for random.seed() in code (should be deterministic)
3. Validate on multiple datasets

---

## 📊 Google Colab Verification

If you trained on Colab, verify before downloading:

```python
# After training completes, run in Colab:

# 1. Upload test_pt_model.py to Colab
from google.colab import files
uploaded = files.upload()  # Select test_pt_model.py

# 2. Run quick test
!python test_pt_model.py --quick

# 3. If passed, run full validation
!python test_pt_model.py

# 4. If all tests pass, download model
files.download('best_model.pt')
```

---

## ✅ Final Checklist

Before considering your model "accurate":

- [ ] `test_pt_model.py` shows: "🎉 ALL TESTS PASSED!"
- [ ] Winning dataset F1 > 0.70
- [ ] All datasets show Premium = 0
- [ ] Precision and Recall both > 0.70
- [ ] Score > 0.70
- [ ] Model loads without errors
- [ ] Logging format is correct
- [ ] Tested on all 4 datasets (easy, medium, extreme, winning)

**If all ✅:** Your model is accurate and ready for submission! 🎉

---

## 🎯 Minimum Acceptable Performance

| Metric | Minimum | Good | Excellent |
|--------|---------|------|-----------|
| F1 (Winning) | 0.70 | 0.80 | 0.90+ |
| Precision | 0.70 | 0.85 | 0.95+ |
| Recall | 0.70 | 0.80 | 0.90+ |
| Score | 0.70 | 0.80 | 0.90+ |
| Premium Penalty | **0** | **0** | **0** |

**Do not submit if:**
- F1 < 0.70 on winning dataset
- Premium penalty > 0
- Any test fails

---

## 📚 Additional Resources

- **Understanding metrics:** `AGENT_ACCURACY_GUIDE.md`
- **Improving performance:** `DQN_TRAINING_GUIDE.md`
- **Troubleshooting:** `GPU_TRAINING_SUMMARY.md`
- **Integration testing:** `INTEGRATION_CHECKLIST.md`

---

## 🚀 Quick Summary

**To check accuracy:**
```bash
python test_pt_model.py
```

**Look for:**
- ✅ "ALL TESTS PASSED!"
- ✅ F1 > 0.70
- ✅ Premium = 0

**If not met:**
- Retrain with more episodes
- Adjust hyperparameters
- Check premium protection logic

**Bottom line:** If `test_pt_model.py` shows all tests passed, your model is accurate! 🎉
