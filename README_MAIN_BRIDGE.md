# 🚀 main.py - Agent Integration Bridge

## Overview

`main.py` is the **production-ready entry point** that connects trained agents to the API Rate Limit Defender environment for Meta OpenEnv submission. It handles:

- ✅ Multi-task execution (3 tasks)
- ✅ Strict Meta-compliant logging
- ✅ Error handling and validation
- ✅ Final performance summary
- ✅ Support for multiple agent types

---

## 🎯 Features

### 1. **Multi-Task Execution**
Automatically runs all 3 tasks:
- `easy-triage` (10 users, easy dataset)
- `behavioral-analysis` (20 users, medium dataset)
- `adversarial-defense` (83 users, winning dataset with seed=42)

### 2. **Meta-Strict Logging**
Produces exact format required by Meta evaluator:
```
[START] task=<task_id> env=api-defender model=<agent_name>
[STEP] step=<n> action=<action_str> reward=<0.00> done=<bool> error=<msg|null>
[END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...>
```

### 3. **Robust Error Handling**
- Invalid user_id → defaults to `noop`, logs error
- Already blocked user → defaults to `noop`, logs error
- Agent crashes → defaults to `noop`, continues execution
- Premium blocking prevention (hard constraint)

### 4. **Three Agent Types Supported**

#### **Option 1: Heuristic Agent** (Default)
```python
agent = HeuristicAgent(rps_threshold=50, name="Heuristic-v1")
```
- No training required
- Good baseline (F1 ~0.70-0.75)
- Fast and deterministic

#### **Option 2: LLM Agent**
```python
agent = LLMAgent(name="GPT-Defender")
```
- Uses OpenAI-compatible API
- Requires environment variables:
  ```bash
  export OPENAI_API_KEY="your-key"
  export API_BASE_URL="http://localhost:8000/v1"
  export MODEL_NAME="gpt-3.5-turbo"
  ```

#### **Option 3: Trained Model Agent** (Sakshi's Agent)
```python
agent = TrainedModelAgent(model_path="sakshi_model.pt", name="Sakshi-DQN-v1")
```
- Load trained PyTorch/TensorFlow model
- Customize `_extract_features()` for your model
- Customize `_predict()` for your model architecture

---

## 📖 Usage

### **Quick Start**
```bash
cd "c:\Users\Dewpearl Gonsalves\meta"
python main.py
```

### **Output Example**
```
======================================================================
API Rate Limit Defender - Agent Integration Bridge
======================================================================
Agent: Heuristic-v1
======================================================================

[START] task=easy-triage env=api-defender model=Heuristic-v1
[STEP] step=1 action=block(U8) reward=0.50 done=False error=null
[STEP] step=2 action=block(U9) reward=0.50 done=False error=null
[STEP] step=3 action=block(U10) reward=0.50 done=False error=null
[STEP] step=4 action=noop reward=0.00 done=True error=null
[END] success=true steps=4 score=0.923 rewards=0.50,0.50,0.50,0.00

[START] task=behavioral-analysis env=api-defender model=Heuristic-v1
[STEP] step=1 action=block(U15) reward=0.50 done=False error=null
...

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
  Premium Blocked: 0
  Total Reward:   1.50
...
```

---

## 🔧 Customization Guide

### **1. Integrate Sakshi's Trained Agent**

**Step 1:** Open `main.py`, find the agent selection section (~line 560):

```python
# Option 3: Trained PyTorch model (Sakshi's trained agent)
agent = TrainedModelAgent(model_path="sakshi_model.pt", name="Sakshi-DQN-v1")
```

**Step 2:** Customize feature extraction in `TrainedModelAgent._extract_features()`:

```python
def _extract_features(self, user: Dict, observation: Dict) -> Any:
    """Extract features matching Sakshi's training."""
    import torch
    
    # Match the features Sakshi used during training
    features = [
        user["rps"] / 100.0,              # Normalized RPS
        float(user["is_suspicious_pattern"]),
        float(user["tier"] == "premium"),
        observation["system_health"],
        len(observation["blocked_users"]) / max(len(observation["users"]), 1)
    ]
    
    return torch.tensor(features, dtype=torch.float32)
```

**Step 3:** Customize prediction in `TrainedModelAgent._predict()`:

```python
def _predict(self, features) -> float:
    """Get block probability from model."""
    import torch
    with torch.no_grad():
        output = self.model(features)
        # If model outputs logits, apply sigmoid
        prob = torch.sigmoid(output).item()
        return prob
```

**Step 4:** Place model file in the project directory:
```bash
cp sakshi_model.pt "c:\Users\Dewpearl Gonsalves\meta\"
```

**Step 5:** Run:
```bash
python main.py
```

---

### **2. Add Custom Agent**

Create a new agent class:

```python
class MyCustomAgent(BaseAgent):
    """Your custom agent implementation."""
    
    def __init__(self, name: str = "MyAgent"):
        self.name = name
        # Initialize your agent
    
    def get_name(self) -> str:
        return self.name
    
    def select_action(self, observation: Dict[str, Any]) -> Action:
        """Your decision logic here."""
        users = observation.get("users", [])
        blocked_users = set(observation.get("blocked_users", []))
        
        for user in users:
            if user["id"] in blocked_users:
                continue
            
            # CRITICAL: Never block premium
            if user["tier"] == "premium":
                continue
            
            # Your logic here
            if self.should_block(user):
                return Action(type="block", user_id=user["id"])
        
        return Action(type="noop", user_id=None)
    
    def should_block(self, user: Dict) -> bool:
        """Your custom blocking logic."""
        # Example: more sophisticated rules
        risk_score = 0.0
        
        if user["rps"] > 100:
            risk_score += 0.5
        elif user["rps"] > 50:
            risk_score += 0.3
        
        if user["is_suspicious_pattern"]:
            risk_score += 0.4
        
        return risk_score > 0.7
```

Then in `main()`:
```python
agent = MyCustomAgent(name="CustomAgent-v1")
```

---

### **3. Modify Task Configuration**

Edit `TASKS` list at the top of `main.py`:

```python
TASKS = [
    TaskConfig(
        task_id="easy-triage",
        task_name="Easy Triage",
        dataset_fn=get_easy_data,
        seed=None  # No seed for easy
    ),
    TaskConfig(
        task_id="behavioral-analysis",
        task_name="Behavioral Analysis",
        dataset_fn=get_medium_data,
        seed=None
    ),
    TaskConfig(
        task_id="adversarial-defense",
        task_name="Adversarial Defense",
        dataset_fn=get_winning_data,
        seed=42  # Seed for reproducibility
    ),
    # Add more tasks if needed
]
```

---

## 🎯 Validation Checklist

Before submission, ensure:

- [ ] **No premium users blocked** (premium_penalty = 0)
- [ ] **F1 > 0.70** on all tasks
- [ ] **System health > 80%** average
- [ ] **All tasks complete** (success = true)
- [ ] **Logging format matches** Meta requirements
- [ ] **Error handling works** (test invalid user_ids)
- [ ] **Deterministic** (same results on repeated runs)

---

## 🐛 Troubleshooting

### **Issue: Agent blocks premium users**
**Solution:** Check agent's `select_action()`:
```python
if user["tier"] == "premium":
    continue  # NEVER block premium
```

### **Issue: Invalid user_id errors**
**Solution:** The bridge automatically handles this and defaults to `noop`. Check error log in final summary.

### **Issue: Model not loading**
**Solution:** Verify model path and PyTorch installation:
```bash
pip install torch
python -c "import torch; print(torch.__version__)"
```

### **Issue: Logging format wrong**
**Solution:** Don't modify `ExecutionEngine.run_task()` - it already matches Meta format.

---

## 📊 Expected Results

### **Heuristic Agent (Baseline)**
| Task | F1 | Precision | Recall | Score |
|------|-----|-----------|--------|-------|
| Easy | 0.95+ | 1.00 | 0.95+ | 0.92+ |
| Medium | 0.75 | 0.85 | 0.70 | 0.72 |
| Hard | 0.70 | 0.80 | 0.65 | 0.68 |

### **Trained RL Agent (Target)**
| Task | F1 | Precision | Recall | Score |
|------|-----|-----------|--------|-------|
| Easy | 0.95+ | 1.00 | 0.95+ | 0.92+ |
| Medium | 0.85+ | 0.90+ | 0.82+ | 0.82+ |
| Hard | 0.82+ | 0.88+ | 0.78+ | 0.80+ |

---

## 🚀 Deployment

### **Local Testing**
```bash
python main.py
```

### **Docker Deployment**
```bash
docker build -t api-defender .
docker run api-defender
```

### **Hugging Face Spaces**
```bash
# Already configured in Dockerfile
# Just push to HF repo
```

---

## 📚 Key Classes

### **BaseAgent**
Interface all agents must implement:
- `get_name()` → str
- `select_action(observation)` → Action
- `reset()` → optional

### **Action** (Pydantic Model)
```python
Action(type="block", user_id="U123")  # Block user
Action(type="noop", user_id=None)     # Do nothing
```

### **ExecutionEngine**
Manages task execution:
- `run_task(task)` → Dict with results
- `run_all_tasks()` → List of results
- `print_final_summary(results)` → Pretty print

---

## ✅ Integration Tests

Run validation before submission:

```bash
# Test all agent types
python main.py

# Test with different agents
# Edit main.py, change agent = ...
python main.py

# Verify output format
python main.py > output.log
cat output.log | grep "\[START\]"
cat output.log | grep "\[STEP\]"
cat output.log | grep "\[END\]"
```

---

## 🎓 Architecture

```
main.py
├── TaskConfig (3 tasks)
├── BaseAgent (interface)
│   ├── HeuristicAgent
│   ├── LLMAgent
│   └── TrainedModelAgent
└── ExecutionEngine
    ├── run_task()
    │   ├── env.reset(dataset)
    │   ├── agent.select_action(obs)
    │   ├── validate_action()
    │   └── env.step(action)
    └── print_final_summary()
```

---

## 🔑 Key Points

1. **Never modify reward formula** - uses `Grader` class (matches evaluator.py)
2. **Strict logging format** - matches Meta requirements exactly
3. **Error handling** - defaults to noop, never crashes
4. **Premium protection** - hard constraint, never block premium
5. **Modular design** - easy to swap agents
6. **Comprehensive validation** - checks all requirements

---

## 📞 Support

If you encounter issues:
1. Check error log in final summary
2. Verify agent's `select_action()` implementation
3. Test with `HeuristicAgent` first (known working baseline)
4. Review `AGENT_ACCURACY_GUIDE.md` for improvement tips

---

**Ready to submit!** 🎯

All requirements met:
✅ Multi-task execution  
✅ Meta-strict logging  
✅ Error handling  
✅ Agent bridge  
✅ Validation  
✅ Production-ready
