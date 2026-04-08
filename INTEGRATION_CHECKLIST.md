# ✅ Agent Integration Checklist

Use this checklist to integrate your trained agent with `main.py`.

---

## 📋 Pre-Integration Checklist

- [ ] **Model is trained** and saved to a file (e.g., `best_model.pt`)
- [ ] **Model architecture is documented** (input dim, hidden layers, output dim)
- [ ] **Feature extraction is clear** (which features were used during training)
- [ ] **Model achieves target metrics** (F1 > 0.80 on validation set)
- [ ] **PyTorch is installed** (`pip install torch`)

---

## 🔧 Integration Steps

### **Step 1: Prepare Your Model File**

- [ ] Save model to project directory:
  ```bash
  cp your_model.pt "c:\Users\Dewpearl Gonsalves\meta\best_model.pt"
  ```

- [ ] Verify model loads correctly:
  ```python
  import torch
  model = torch.load("best_model.pt", map_location="cpu")
  print(model)  # Should print model architecture
  ```

---

### **Step 2: Choose Integration Method**

**Option A: Use `sakshi_agent_example.py` (Recommended)**

- [ ] Copy `sakshi_agent_example.py` to your working file
- [ ] Update model path in `SakshiAgent.__init__()`
- [ ] Customize `_extract_features()` to match your training features
- [ ] Customize `_predict()` to match your model output format
- [ ] Update `confidence_threshold` (default 0.7)

**Option B: Modify `main.py` directly**

- [ ] Open `main.py`
- [ ] Find `TrainedModelAgent` class
- [ ] Update `_extract_features()` method
- [ ] Update `_predict()` method
- [ ] Update `model_path` in `main()` function

---

### **Step 3: Verify Feature Extraction**

- [ ] Features match training exactly (order, normalization, scaling)
- [ ] Test feature extraction:
  ```python
  from sakshi_agent_example import test_feature_extraction
  test_feature_extraction()
  ```

- [ ] Expected output:
  ```
  Feature shape: torch.Size([10])
  Feature values: tensor([0.50, 1.00, 0.00, ...])
  Block confidence: 0.823
  Action: block (U1)
  ```

---

### **Step 4: Test on Single Task**

- [ ] Run single task test:
  ```python
  from sakshi_agent_example import test_on_single_task
  test_on_single_task()
  ```

- [ ] Check results:
  ```
  Step 1: block(U8) -> reward=0.50
  Step 2: block(U9) -> reward=0.50
  ...
  Results:
    F1:       0.950
    Score:    0.923
    Rewards:  1.50
  ```

- [ ] Verify:
  - [ ] No crashes or errors
  - [ ] Agent blocks some users (not all noop)
  - [ ] F1 > 0.70
  - [ ] No premium users blocked (premium_penalty = 0)

---

### **Step 5: Test Premium Protection**

- [ ] Create test with premium users:
  ```python
  observation = {
      "users": [
          {"id": "U1", "rps": 200, "is_suspicious_pattern": True, "tier": "premium"},
          {"id": "U2", "rps": 200, "is_suspicious_pattern": True, "tier": "normal"}
      ],
      "blocked_users": [],
      "system_health": 1.0
  }
  
  from sakshi_agent_example import SakshiAgent
  agent = SakshiAgent("best_model.pt")
  action = agent.select_action(observation)
  
  # Should block U2 (normal), NOT U1 (premium)
  assert action.user_id == "U2", "Agent blocked premium user!"
  print("✅ Premium protection works!")
  ```

- [ ] Agent NEVER blocks premium users

---

### **Step 6: Full Multi-Task Execution**

- [ ] Run full integration:
  ```bash
  python sakshi_agent_example.py
  ```

- [ ] Check all 3 tasks complete:
  ```
  [START] task=easy-triage env=api-defender model=Sakshi-DQN-v1
  [STEP] step=1 action=block(U8) reward=0.50 done=False error=null
  ...
  [END] success=true steps=4 score=0.923 rewards=0.50,0.50,0.50,0.00
  
  [START] task=behavioral-analysis ...
  [START] task=adversarial-defense ...
  
  FINAL_SUMMARY
  ```

- [ ] Verify final results:
  - [ ] All tasks: success=true
  - [ ] Average F1 > 0.70 (target: 0.80+)
  - [ ] Average system health > 80%
  - [ ] Total premium blocked = 0
  - [ ] No crashes or exceptions

---

## 🎯 Performance Targets

| Metric | Minimum | Good | Excellent |
|--------|---------|------|-----------|
| Easy F1 | 0.90 | 0.95 | 0.98+ |
| Medium F1 | 0.70 | 0.80 | 0.85+ |
| Hard F1 | 0.65 | 0.75 | 0.82+ |
| Avg Score | 0.65 | 0.75 | 0.85+ |
| System Health | 80% | 90% | 95%+ |
| Premium Blocked | **0** | **0** | **0** |

---

## 🐛 Common Issues

### **Issue 1: Model not loading**
```python
# Error: Can't load model file
```

**Solution:**
- [ ] Check file path is correct
- [ ] Check PyTorch version matches training version
- [ ] Try loading with `map_location="cpu"`:
  ```python
  model = torch.load("best_model.pt", map_location="cpu")
  ```

---

### **Issue 2: Feature dimension mismatch**
```python
# Error: Expected input [1, 10] but got [1, 8]
```

**Solution:**
- [ ] Count features in `_extract_features()`
- [ ] Match exactly with training features
- [ ] Check feature order matches training

---

### **Issue 3: Agent blocks premium users**
```python
# premium_penalty > 0 in results
```

**Solution:**
- [ ] Add hard constraint in `select_action()`:
  ```python
  if user["tier"] == "premium":
      continue  # NEVER block premium
  ```

---

### **Issue 4: All actions are noop**
```python
# Agent never blocks anyone
```

**Solution:**
- [ ] Check confidence threshold (try lowering: 0.7 → 0.5)
- [ ] Check `_predict()` returns values in [0, 1]
- [ ] Print intermediate predictions to debug
- [ ] Verify model actually learned (test on easy data first)

---

### **Issue 5: Low F1 score**
```python
# F1 < 0.70
```

**Solution:**
- [ ] Check if agent is too conservative (high precision, low recall)
  - → Lower confidence threshold
- [ ] Check if agent is too aggressive (low precision, high recall)
  - → Raise confidence threshold
- [ ] Review AGENT_ACCURACY_GUIDE.md for improvement tips
- [ ] Try curriculum training (easy → medium → hard)

---

## 📊 Logging Verification

Check that logs match exact format:

- [ ] `[START]` format:
  ```
  [START] task=<task_id> env=api-defender model=<name>
  ```

- [ ] `[STEP]` format:
  ```
  [STEP] step=<n> action=<type>(<id>) reward=<0.00> done=<bool> error=<msg|null>
  ```

- [ ] `[END]` format:
  ```
  [END] success=<bool> steps=<n> score=<0.000> rewards=<r1,r2,...>
  ```

- [ ] Rewards formatted to 2 decimals (0.50, -0.10)
- [ ] Score formatted to 3 decimals (0.923)
- [ ] Boolean lowercase (true/false not True/False)

---

## 🚀 Submission Checklist

Before final submission:

- [ ] **All tests pass** (steps 1-6 above)
- [ ] **No premium users blocked** across all tasks
- [ ] **F1 > 0.70** on all 3 tasks
- [ ] **Logging format correct** (matches Meta requirements)
- [ ] **Code is clean** (no debug prints, no commented code)
- [ ] **README updated** with your agent name and approach
- [ ] **Model file included** in submission package
- [ ] **requirements.txt updated** with any new dependencies
- [ ] **Tested on fresh environment** (clean Python install)

---

## 📦 Submission Package

Your final submission should include:

```
meta/
├── main.py                    # Integration bridge (unchanged)
├── sakshi_agent_example.py    # Your agent implementation
├── best_model.pt              # Your trained model
├── environment.py             # Environment (unchanged)
├── grader.py                  # Grader (unchanged)
├── openenv_models.py          # Models (unchanged)
├── data.py                    # Data (unchanged)
├── requirements.txt           # Updated with torch
├── README_MAIN_BRIDGE.md      # Documentation
└── AGENT_ACCURACY_GUIDE.md    # Training guide
```

---

## ✅ Final Validation

Run this final test:

```bash
# Clean test
python -m pytest test_environment.py -v

# Full integration test
python sakshi_agent_example.py > output.log 2>&1

# Check results
cat output.log | grep "FINAL_SUMMARY" -A 20
```

Expected output:
```
FINAL_SUMMARY
======================================================================

Task: Easy Triage (easy-triage)
  Success:        True
  Final Score:    0.923
  Premium Blocked: 0

Task: Behavioral Analysis (behavioral-analysis)
  Success:        True
  Final Score:    0.812
  Premium Blocked: 0

Task: Adversarial Defense (adversarial-defense)
  Success:        True
  Final Score:    0.798
  Premium Blocked: 0

======================================================================
VALIDATION
======================================================================
✅ No premium blocked:     True
✅ Avg F1 > 0.70:          True
✅ Avg health > 80%:       True
✅ All tasks completed:    True
```

---

## 🎉 Success Criteria

**You're ready to submit when:**

✅ All checkboxes above are checked  
✅ No errors in test runs  
✅ Performance meets minimum targets  
✅ Logging format is exact  
✅ Premium protection is verified  

**Congratulations!** 🎊 Your agent is integrated and ready for Meta OpenEnv submission!

---

## 📞 Need Help?

1. **Feature extraction issues** → Check training logs for exact features used
2. **Model loading issues** → Verify PyTorch version compatibility
3. **Performance issues** → Review `AGENT_ACCURACY_GUIDE.md`
4. **Integration issues** → Follow `README_MAIN_BRIDGE.md` step by step

Good luck! 🚀
