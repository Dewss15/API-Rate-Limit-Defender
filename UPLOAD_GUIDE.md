# 📦 File Upload Guide

## For Different Scenarios

---

## 🎯 Scenario 1: Meta OpenEnv Hackathon Submission

### ✅ **REQUIRED FILES (Must Upload)**

```
Core Environment:
├── environment.py          # Main RL environment
├── models.py              # Data contracts (User, Observation, StepInfo)
├── data.py                # Dataset loader (provided by teammate)
├── evaluator.py           # Scoring function (provided by teammate)
└── grader.py              # Score calculator

OpenEnv Compliance:
├── openenv.yaml           # Environment metadata
├── openenv_models.py      # Pydantic models for OpenEnv
└── inference.py           # Main entry point for evaluation

Deployment:
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
└── .dockerignore          # Docker ignore patterns

Agent (Choose ONE):
├── easy_agent_demo.py     # Easy baseline agent
├── medium_agent_demo.py   # Medium baseline agent
├── hard_agent_demo.py     # Hard baseline agent
└── best_model.pt          # Trained DQN model (if using ML)
```

**Total: 13-14 files** (~20 KB + model)

---

## 🧠 Scenario 2: Training & Submitting DQN Model

### ✅ **For Training (Local)**

```
Training Pipeline:
├── train_dqn.py           # DQN training script
├── environment.py         # Environment
├── models.py              # Data models
├── data.py                # Datasets
├── grader.py              # Grading
└── requirements.txt       # Dependencies (including torch)
```

**Run locally:** `python train_dqn.py` → creates `best_model.pt`

### ✅ **For Submission (Upload)**

After training, upload:

```
Trained Model:
├── best_model.pt          # Trained weights (~1-2 MB)

Model Loader:
├── sakshi_agent_example.py  # Or your custom agent
└── openenv_models.py      # Pydantic models

Core Files (same as Scenario 1):
├── environment.py
├── models.py
├── data.py
├── evaluator.py
├── grader.py
├── openenv.yaml
├── inference.py
├── Dockerfile
├── requirements.txt
└── .dockerignore
```

**Total: 12 files** (~25 KB + 1-2 MB model)

---

## 🚀 Scenario 3: Hugging Face Spaces Deployment

### ✅ **Required Files**

```
Deployment:
├── app.py                 # Gradio/Streamlit app (you need to create)
├── Dockerfile             # Already created
├── requirements.txt       # Already created
└── .dockerignore          # Already created

Model & Environment:
├── best_model.pt          # Trained model
├── environment.py         # Environment
├── models.py              # Models
├── data.py                # Datasets
├── grader.py              # Grading
├── openenv.yaml           # Metadata
└── inference.py           # Inference logic

Agent:
└── sakshi_agent_example.py  # Agent implementation
```

---

## 📋 Complete File Checklist

### ✅ **Core Files (Always Upload)**

| File | Size | Required? | Purpose |
|------|------|-----------|---------|
| `environment.py` | 8.4 KB | ✅ Yes | Main RL environment |
| `models.py` | 3.9 KB | ✅ Yes | Data contracts |
| `data.py` | 6.2 KB | ✅ Yes | Dataset loader |
| `evaluator.py` | 2.2 KB | ✅ Yes | External evaluator |
| `grader.py` | 6.5 KB | ✅ Yes | Score calculator |
| `openenv.yaml` | 4.2 KB | ✅ Yes | Environment metadata |
| `openenv_models.py` | 2.4 KB | ✅ Yes | Pydantic models |
| `inference.py` | 9.9 KB | ✅ Yes | Entry point |
| `Dockerfile` | 1.3 KB | ✅ Yes | Container config |
| `requirements.txt` | ~0.4 KB | ✅ Yes | Dependencies |
| `.dockerignore` | 0.3 KB | ✅ Yes | Docker ignore |

**Subtotal: 11 files (~45 KB)**

---

### 🤖 **Agent Files (Choose ONE Set)**

**Option A: Heuristic Agent (No ML)**
```
├── easy_agent_demo.py      # 5.2 KB - Simple heuristic
├── medium_agent_demo.py    # 6.8 KB - Smarter heuristic
└── hard_agent_demo.py      # 8.1 KB - Advanced heuristic
```
Pick one: **1 file (~5-8 KB)**

**Option B: DQN Agent (Trained ML)**
```
├── best_model.pt           # 1-2 MB - Trained weights
├── sakshi_agent_example.py # 12.2 KB - Agent wrapper
└── train_dqn.py            # Optional - for retraining
```
Upload: **2 files (~1.2 MB + 12 KB)**

**Option C: Custom Agent**
```
└── your_custom_agent.py    # Your implementation
```

---

### 📚 **Documentation (Optional)**

| File | Size | Upload? | Purpose |
|------|------|---------|---------|
| `README_AGENT.md` | 15.4 KB | 📖 Optional | Agent developer guide |
| `README_TESTING.md` | 5.1 KB | 📖 Optional | Testing guide |
| `README_OPENENV.md` | 10.0 KB | 📖 Optional | OpenEnv guide |
| `README_MAIN_BRIDGE.md` | 11.2 KB | 📖 Optional | Integration docs |
| `DQN_TRAINING_GUIDE.md` | 14.7 KB | 📖 Optional | Training guide |
| `GPU_SETUP_GUIDE.md` | 10.6 KB | 📖 Optional | GPU setup |
| `AGENT_ACCURACY_GUIDE.md` | 23.6 KB | 📖 Optional | Improvement tips |

**Upload README.md if required by platform**

---

### 🚫 **Do NOT Upload (Local Development Only)**

| File | Why Not? |
|------|----------|
| `__pycache__/` | Python cache (regenerated) |
| `*.pyc` | Compiled Python (regenerated) |
| `.git/` | Git history (unnecessary) |
| `test_*.py` | Local tests (not needed in prod) |
| `example_usage.py` | Local demo (not needed) |
| `validate_openenv.py` | Local validation (not needed) |
| `quick_test.py` | Local testing (not needed) |
| `check_gpu.py` | Local GPU check (not needed) |
| `check_gpu.bat` | Windows helper (not needed) |
| `*.md` | Documentation (optional) |
| `.gitignore` | Git config (not needed) |

---

## 🎯 **Minimum Upload (Smallest Set)**

**For basic submission:**

```
Core (11 files):
environment.py, models.py, data.py, evaluator.py, grader.py,
openenv.yaml, openenv_models.py, inference.py,
Dockerfile, requirements.txt, .dockerignore

Agent (1 file):
hard_agent_demo.py  OR  best_model.pt + sakshi_agent_example.py

Total: 12-13 files (~50 KB or ~1.2 MB with ML)
```

---

## 📦 **Recommended Upload (Best Practice)**

```
Core (11 files):
environment.py, models.py, data.py, evaluator.py, grader.py,
openenv.yaml, openenv_models.py, inference.py,
Dockerfile, requirements.txt, .dockerignore

Agent (2 files):
best_model.pt, sakshi_agent_example.py

Integration (1 file):
main.py  # For local testing before submission

Documentation (1 file):
README.md  # Create one with:
  - Project description
  - How to run
  - Model performance

Total: 15 files (~1.3 MB)
```

---

## 🔍 **File Upload Priority**

### **Priority 1: Critical (Cannot run without these)**
1. `environment.py`
2. `models.py`
3. `data.py`
4. `evaluator.py`
5. `grader.py`
6. `openenv.yaml`
7. `inference.py`
8. `requirements.txt`

### **Priority 2: Important (Needed for deployment)**
9. `Dockerfile`
10. `.dockerignore`
11. `openenv_models.py`

### **Priority 3: Agent (Choose based on approach)**
12. `best_model.pt` + `sakshi_agent_example.py` (if using ML)
   OR `hard_agent_demo.py` (if using heuristic)

### **Priority 4: Optional (Helpful but not required)**
- `main.py` (for integration testing)
- `README.md` (documentation)
- Other markdown files (guides)

---

## 📤 **Platform-Specific Guides**

### **Hugging Face Spaces**

Upload via web interface or Git:

```bash
# Create repository on Hugging Face
# Then clone and add files:

git clone https://huggingface.co/spaces/your-username/api-defender
cd api-defender

# Copy essential files
cp environment.py models.py data.py evaluator.py grader.py .
cp openenv.yaml openenv_models.py inference.py .
cp Dockerfile requirements.txt .dockerignore .
cp best_model.pt sakshi_agent_example.py .  # If using ML

# Create README.md with project info
# Then push:
git add .
git commit -m "Initial commit"
git push
```

### **Google Colab / Kaggle**

Upload via notebook interface:
1. Click "Upload" button
2. Select files from the **Minimum Upload** list
3. Run training or inference

### **Submission Portal (e.g., Meta OpenEnv)**

Check requirements, but typically:
- **All files** from **Core** section
- **Agent** (best_model.pt or heuristic)
- **Optional:** README.md with instructions

---

## ✅ **Pre-Upload Checklist**

Before uploading, verify:

- [ ] All Priority 1 files included
- [ ] Agent file(s) included (model or heuristic)
- [ ] `requirements.txt` has all dependencies
- [ ] `Dockerfile` is present
- [ ] No `__pycache__` or `.pyc` files
- [ ] No local test files
- [ ] Model file < 10 MB (if applicable)
- [ ] Total upload < 50 MB

---

## 🎯 **Quick Reference**

**For hackathon submission:**
```bash
# Create submission folder
mkdir submission
cd submission

# Copy core files
cp ../environment.py ../models.py ../data.py ../evaluator.py ../grader.py .
cp ../openenv.yaml ../openenv_models.py ../inference.py .
cp ../Dockerfile ../requirements.txt ../.dockerignore .

# Copy agent (choose one):
cp ../best_model.pt ../sakshi_agent_example.py .  # ML agent
# OR
cp ../hard_agent_demo.py .  # Heuristic agent

# Verify
ls -lh
# Should see 12-13 files, ~50 KB or ~1.3 MB

# Create README.md
echo "# API Rate Limit Defender" > README.md
echo "DQN agent for bot detection" >> README.md

# Create archive (if needed)
zip -r submission.zip .
```

---

## 📊 **File Size Reference**

| Category | Files | Total Size |
|----------|-------|------------|
| Core Environment | 11 | ~45 KB |
| Heuristic Agent | 1 | ~8 KB |
| DQN Agent | 2 | ~1.2 MB |
| Documentation | 7 | ~90 KB |
| **Minimum Submission** | **12** | **~53 KB** |
| **With DQN Model** | **13** | **~1.3 MB** |
| **Everything** | **45** | **~2 MB** |

---

## 💡 **Pro Tips**

1. **Test locally first:**
   ```bash
   python inference.py
   # OR
   python main.py
   ```

2. **Validate before upload:**
   ```bash
   python validate_openenv.py
   ```

3. **Check file sizes:**
   ```bash
   ls -lh *.py *.yaml *.pt 2>/dev/null | sort -k5 -h
   ```

4. **Create clean archive:**
   ```bash
   # On Windows
   Compress-Archive -Path environment.py,models.py,... -DestinationPath submission.zip
   
   # On Linux/Mac
   tar -czf submission.tar.gz environment.py models.py ...
   ```

---

## 🚀 **Ready to Upload?**

**Minimum set (53 KB):**
- 11 core files + 1 heuristic agent

**Recommended set (1.3 MB):**
- 11 core files + DQN model + agent wrapper + main.py

**Choose based on:**
- Hackathon rules (check size limits)
- Deployment platform (Hugging Face, Colab, etc.)
- Performance goals (heuristic vs ML)

---

**Questions? Check:**
- `SUBMISSION_READY.md` - Final checklist
- `README_OPENENV.md` - OpenEnv requirements
- Platform documentation for specific upload instructions
