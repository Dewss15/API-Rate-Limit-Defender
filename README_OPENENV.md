# 🚀 OpenEnv Submission Guide

## ✅ **What Was Created**

All files required for OpenEnv compliance and hackathon submission:

### 📦 Core Files

| File | Purpose | Status |
|------|---------|--------|
| `openenv_models.py` | Pydantic v2 data contracts | ✅ Complete |
| `openenv.yaml` | Environment metadata & tasks | ✅ Complete |
| `grader.py` | Exact evaluator.py mirror | ✅ Validated |
| `inference.py` | Inference entry point with strict logging | ✅ Complete |
| `requirements.txt` | Python dependencies | ✅ Complete |
| `Dockerfile` | Container setup | ✅ Complete |
| `validate_openenv.py` | Pre-submission validation | ✅ Complete |

---

## 🔍 **Pre-Submission Checklist**

Run the validation script before submitting:

```bash
python validate_openenv.py
```

This checks:
- ✅ All required files exist
- ✅ `openenv.yaml` structure is valid
- ✅ Pydantic models work correctly
- ✅ Environment hides `is_bot` from observations
- ✅ Grader matches `evaluator.py` EXACTLY
- ✅ Inference script can run all three tasks
- ✅ System health formula is correct
- ✅ JSON logging format is strict

---

## 🧪 **Local Testing**

### Test 1: Run Inference with Heuristic Agent

```bash
python inference.py
```

Expected output (JSON format):
```json
{"event": "INIT", "message": "Starting OpenEnv inference"}
{"event": "INFO", "agent": "Heuristic"}
{"event": "START", "task": "easy-triage"}
{"event": "STEP", "step": 1, "action": {...}, "reward": 0.5, "done": false}
...
{"event": "END", "task": "easy-triage", "final_score": 0.85, "tp": 3, "fp": 0, "fn": 0}
...
{"event": "COMPLETE"}
```

### Test 2: Verify Grader

```bash
python grader.py
```

Expected output:
```
=== Grader Verification ===
Blocked: 3 users
TP=3, FP=0, FN=0, TN=7
F1=1.0000, Health=1.0000
Score=0.9000
✅ Grader matches evaluator.py EXACTLY
```

### Test 3: Docker Build

```bash
docker build -t api-rate-limit-defender .
```

### Test 4: Docker Run

```bash
docker run api-rate-limit-defender
```

---

## 📊 **File Details**

### 1. **openenv_models.py** - Type Safety

Defines Pydantic v2 models:

```python
class UserObservation(BaseModel):
    id: str
    rps: int
    is_suspicious_pattern: bool
    tier: Literal["normal", "premium"]

class Observation(BaseModel):
    users: List[UserObservation]
    blocked_users: List[str]
    system_health: float

class Action(BaseModel):
    type: Literal["block", "noop"]
    user_id: Optional[str]
```

**Key feature:** `is_bot` is NOT included in `UserObservation`

---

### 2. **openenv.yaml** - Environment Metadata

Defines:
- Environment name and version
- Observation/action space specifications
- Three tasks:
  - `easy-triage` (10 users, obvious patterns)
  - `behavioral-analysis` (20 users, moderate)
  - `adversarial-defense` (83 users, hard)
- Evaluation formula
- Target metrics for each task

---

### 3. **grader.py** - Exact Evaluator Mirror

**CRITICAL:** Formula matches `evaluator.py` exactly:

```python
score = (0.6 * f1) + (0.3 * system_health) - (0.1 * premium_penalty_rate)
```

Includes validation method to verify against original evaluator.

---

### 4. **inference.py** - Entry Point

Two agent modes:

#### Heuristic Agent (Default)
```bash
python inference.py
```

#### LLM Agent (Optional)
```bash
export USE_LLM=true
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-3.5-turbo"
export HF_TOKEN="your_token"
python inference.py
```

**Log Format:** STRICT JSON for grading:
```json
{"event": "START", "task": "task_name"}
{"event": "STEP", "step": 1, "action": {...}, "reward": 0.4, "done": false}
{"event": "END", "task": "task_name", "final_score": 0.85, "tp": 3, "fp": 0, "fn": 0}
```

---

### 5. **Dockerfile** - Containerization

Multi-stage build:
- Stage 1: Build dependencies
- Stage 2: Minimal runtime

Default command: `python inference.py`

Environment variables:
- `API_BASE_URL` - OpenAI-compatible endpoint
- `MODEL_NAME` - Model identifier
- `HF_TOKEN` - Authentication token
- `USE_LLM` - Enable LLM agent (default: false)

---

### 6. **validate_openenv.py** - Pre-Submission Validation

Comprehensive checks:
1. ✅ File existence
2. ✅ YAML structure
3. ✅ Pydantic models
4. ✅ Environment compatibility
5. ✅ Grader accuracy
6. ✅ Inference execution

Run before every submission!

---

## 🎯 **Task Specifications**

### Task 1: easy-triage
- **Dataset:** 10 users (7 humans, 3 bots)
- **Difficulty:** Easy
- **Target F1:** > 0.90
- **Target Health:** > 0.95
- **Bots:** Obvious high RPS (400-600) + suspicious patterns

### Task 2: behavioral-analysis
- **Dataset:** 20 users (14 humans, 6 bots)
- **Difficulty:** Medium
- **Target F1:** > 0.80
- **Target Health:** > 0.90
- **Bots:** Some RPS overlap, requires pattern analysis

### Task 3: adversarial-defense
- **Dataset:** 83 users (56 humans, 24 bots, 3 hard cases)
- **Difficulty:** Hard
- **Target F1:** > 0.80
- **Target Health:** > 0.90
- **Challenges:**
  - Stealth bots (low RPS, not suspicious)
  - Premium traps (high RPS + suspicious but human)
  - Confusing humans (high RPS + suspicious)

---

## 📈 **Expected Performance**

### Heuristic Baseline (RPS > 50 + suspicious)

| Task | F1 Score | Health | Score |
|------|----------|--------|-------|
| easy-triage | 0.95-1.00 | 0.95-1.00 | 0.85-0.95 |
| behavioral-analysis | 0.70-0.80 | 0.80-0.90 | 0.65-0.75 |
| adversarial-defense | 0.65-0.75 | 0.75-0.85 | 0.55-0.70 |

### Target for RL Agent

| Task | F1 Score | Health | Score |
|------|----------|--------|-------|
| easy-triage | > 0.95 | > 0.95 | > 0.90 |
| behavioral-analysis | > 0.85 | > 0.90 | > 0.80 |
| adversarial-defense | > 0.85 | > 0.90 | > 0.80 |

---

## 🔧 **Deployment Options**

### Local Execution
```bash
python inference.py
```

### Docker Execution
```bash
docker build -t api-defender .
docker run api-defender
```

### Hugging Face Spaces
1. Create Space on Hugging Face
2. Set Space SDK to "Docker"
3. Upload all files including Dockerfile
4. Set environment variables in Space settings
5. Space will auto-build and run

### OpenEnv Submission
1. Run `python validate_openenv.py`
2. Ensure all checks pass
3. Package files: `openenv.yaml`, `inference.py`, `requirements.txt`, `Dockerfile`
4. Submit via OpenEnv portal

---

## ⚠️ **Critical Compliance Rules**

### 1. Environment Black Box
- ✅ Do NOT modify `environment.py`
- ✅ Do NOT modify `models.py`
- ✅ Do NOT modify `data.py`
- ✅ Do NOT modify `evaluator.py`

### 2. Hidden Information
- ✅ `is_bot` must NEVER be in observations
- ✅ Agent must infer from `rps`, `is_suspicious_pattern`, `tier`

### 3. Grader Accuracy
- ✅ Formula MUST match `evaluator.py` exactly
- ✅ No approximations
- ✅ Validation required

### 4. Logging Format
- ✅ STRICT JSON format
- ✅ Exact field names and order
- ✅ No extra print statements

### 5. Determinism
- ✅ No randomness (unless seeded)
- ✅ Reproducible results
- ✅ No crashes

---

## 🐛 **Troubleshooting**

### Issue: Validation fails on grader check
**Solution:** Run `python grader.py` to see detailed comparison with evaluator

### Issue: Inference crashes
**Solution:** Check that `USE_LLM=false` for heuristic mode if LLM not available

### Issue: Docker build fails
**Solution:** Ensure all files are in the same directory

### Issue: JSON logs malformed
**Solution:** Check `inference.py` - ensure all prints use `json.dumps()` and `flush=True`

### Issue: Wrong scores
**Solution:** Verify grader formula matches evaluator exactly

---

## 📚 **File Dependencies**

```
inference.py
├── environment.py (existing, do not modify)
├── models.py (existing, do not modify)
├── data.py (existing, do not modify)
├── grader.py (new, validates against evaluator.py)
└── openenv_models.py (new, Pydantic types)

grader.py
└── evaluator.py (existing, do not modify)

validate_openenv.py
├── All of the above
└── openenv.yaml (new, metadata)

Dockerfile
├── requirements.txt (new)
└── All Python files
```

---

## ✅ **Final Submission Checklist**

Before submitting:

- [ ] Run `python validate_openenv.py` - all checks pass
- [ ] Run `python inference.py` - completes all 3 tasks
- [ ] Run `python grader.py` - matches evaluator exactly
- [ ] Docker build succeeds
- [ ] Docker run produces valid JSON logs
- [ ] No `is_bot` in observations
- [ ] Premium penalty count is low (< 2 per task)
- [ ] F1 scores meet targets
- [ ] System health > 0.85 on all tasks
- [ ] All files included in submission
- [ ] README/documentation updated

---

## 🎓 **Next Steps for Sakshi (RL Agent)**

The infrastructure is ready! Sakshi can now:

1. **Use existing structure** - Don't modify OpenEnv files
2. **Focus on agent** - Implement in `inference.py` or separate module
3. **Test locally** - Use `python inference.py`
4. **Replace heuristic** - Swap `HeuristicAgent` with RL agent
5. **Maintain interface** - Keep `select_action(observation)` signature
6. **Run validation** - Use `validate_openenv.py` after changes

**Agent Requirements:**
- Input: `observation` dict (no `is_bot`)
- Output: `action` dict with `{"type": "block"|"noop", "user_id": str}`
- Must complete 3 tasks without crashing
- Target F1 > 0.80, Health > 0.90

---

## 🏆 **Success Criteria**

Your submission is ready when:

1. ✅ `validate_openenv.py` passes all checks
2. ✅ All 3 tasks complete successfully
3. ✅ Average score > 0.75
4. ✅ No premium penalties (or < 2 total)
5. ✅ Docker runs without errors
6. ✅ Logs are valid JSON
7. ✅ Grader matches evaluator exactly

---

**You're ready for submission! 🚀**

For questions:
- Environment: Check `README_TESTING.md`
- Agent: Check `README_AGENT.md`
- OpenEnv: Check this file

Good luck! 🎯
