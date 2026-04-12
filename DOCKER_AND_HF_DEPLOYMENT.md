# 🚀 Docker & Hugging Face Deployment Guide

## Quick Summary

Your submission needs to be deployed to **Hugging Face Spaces** using **Docker**. Here's the complete step-by-step process.

---

## 📋 Phase 1: Verify Local Setup (Do This First!)

### Check all required files exist:
```bash
cd "c:\Users\Dewpearl Gonsalves\meta"

# Verify these files exist:
ls -la Dockerfile
ls -la requirements.txt
ls -la inference.py
ls -la environment.py
ls -la models.py
ls -la data.py
ls -la evaluator.py
ls -la grader.py
ls -la hard_defender_agent.py
ls -la openenv_models.py
ls -la openenv.yaml
ls -la app.py
```

**Expected:** All 13 files present ✅

---

## 🐳 Phase 2: Docker Build (Test Locally)

### Step 1: Install Docker
If not already installed:
- Windows: Download from https://www.docker.com/products/docker-desktop
- Mac: `brew install docker`
- Linux: `sudo apt-get install docker.io`

### Step 2: Test Docker Build Locally
```bash
cd "c:\Users\Dewpearl Gonsalves\meta"

# Build Docker image
docker build -t api-defender:latest .

# Expected output:
# ...
# Successfully tagged api-defender:latest
```

### Step 3: Test Docker Image Locally
```bash
# Run the image
docker run api-defender:latest

# Expected output:
# [START] task=easy-triage env=api-defender model=HardDefender-v1.0
# [STEP] step=1 action=block(U5) reward=0.40 done=false error=null
# [END] success=true steps=1 score=1.000 rewards=0.40
```

**If build fails:**
- Check Dockerfile has all dependencies
- Check requirements.txt is complete
- Run: `docker build -t api-defender . 2>&1 | tail -50` to see last 50 lines

**If run fails:**
- Check inference.py for syntax errors
- Check all imports are available
- Verify hard_defender_agent.py exists

---

## 🤗 Phase 3: Hugging Face Spaces Setup

### Step 1: Create Hugging Face Account
1. Go to https://huggingface.co
2. Click "Sign Up"
3. Complete registration
4. Verify email

### Step 2: Create New Space
1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name:** `api-defender` (or similar)
   - **License:** MIT
   - **Select the Space SDK:** Docker
3. Click "Create Space"

**Result:** You get a Space URL like `https://huggingface.co/spaces/YOUR_USERNAME/api-defender`

### Step 3: Clone Space Repository
```bash
# Navigate to a clean directory
cd Desktop

# Clone the space (replace YOUR_USERNAME)
git clone https://huggingface.co/spaces/YOUR_USERNAME/api-defender
cd api-defender
```

---

## 📤 Phase 4: Upload Your Files to HF Space

### Option A: Using Git (Recommended)

```bash
# 1. Copy all your files to the cloned repo
cd api-defender
cp "c:\Users\Dewpearl Gonsalves\meta\*" .

# 2. Verify files are there
ls -la

# 3. Add all files to git
git add .

# 4. Commit
git commit -m "Initial submission with HardDefenderAgent"

# 5. Push to HF Space (wait 5-10 minutes for build)
git push
```

### Option B: Using Web Interface

1. Go to your Space: `https://huggingface.co/spaces/YOUR_USERNAME/api-defender`
2. Click "Files and versions"
3. Click "Add file" → "Upload files"
4. Select all files from `c:\Users\Dewpearl Gonsalves\meta\*.py`
5. Upload Dockerfile, requirements.txt, etc.
6. Wait for Space to rebuild (5-10 minutes)

---

## ⏳ Phase 5: Wait for Space Build

### Monitor Build Progress:

1. Go to your Space URL
2. Watch the build logs:
   - "Building..." (Red indicator) = Building
   - "Running" (Green indicator) = Ready

### Build typically takes:
- Fast: 2-3 minutes
- Normal: 5-10 minutes
- Slow: 10-20 minutes

### Check Build Logs:

Look for messages like:
```
Step 1/15 : FROM python:3.11-slim
Step 2/15 : WORKDIR /app
...
Successfully built <image_id>
```

### If Build Fails:

Check the "Logs" tab for errors like:
- `ModuleNotFoundError` → Check requirements.txt
- `File not found` → Check Dockerfile COPY commands
- `ImportError` → Check Python imports

**Fix and push again:**
```bash
# After fixing files locally
git add .
git commit -m "Fix build error"
git push
# Wait another 5 minutes
```

---

## ✅ Phase 6: Verify Space is Running

### Check Space Status:

1. **Visual Check:**
   - Green "Running" badge = Working ✅
   - Red "Building" badge = Still building
   - Red "error" badge = Build failed ❌

2. **Endpoint Check:**
```bash
# Test the inference endpoint
curl -X POST https://huggingface.co/spaces/YOUR_USERNAME/api-defender/call/inference

# Expected: Returns JSON or file with output
```

3. **Space UI Check:**
   - If Space has `/inference` endpoint, you should see a UI
   - Test by uploading sample input
   - Should return output in official format

---

## 🔍 Phase 7: Official Validation

### Get Validator Script:

The judges will provide `validate-submission.sh`. When you get it:

```bash
# Make it executable
chmod +x validate-submission.sh

# Run validation (replace with your Space URL)
./validate-submission.sh https://huggingface.co/spaces/YOUR_USERNAME/api-defender

# Expected output:
# ✅ Check 1: Format Compliance... PASS
# ✅ Check 2: Performance Threshold... PASS  
# ✅ Check 3: Premium Protection... PASS
# 
# 🏆 All checks passed!
```

### What the validator checks:

1. **Format Compliance:** Output matches `[START]` `[STEP]` `[END]` format
2. **Performance:** F1 Score >= 0.70
3. **Premium Protection:** Zero premium user violations

### If validation fails:

- **Format error:** Fix inference.py output format
- **Performance error:** Improve agent logic
- **Premium error:** Ensure no premium users get blocked

Then push fixes and re-validate.

---

## 📊 Complete Docker File Checklist

Your `Dockerfile` should have:

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY *.py .
COPY openenv.yaml .

# Set entry point to inference.py
CMD ["python", "inference.py"]
```

✅ Verify in `c:\Users\Dewpearl Gonsalves\meta\Dockerfile`

---

## 📦 Complete requirements.txt Checklist

Should include:

```
streamlit>=1.28.0
pandas>=2.0.0
openenv-core>=0.1.0
pydantic>=2.0.0
```

✅ Verify in `c:\Users\Dewpearl Gonsalves\meta\requirements.txt`

---

## 🎯 Complete Process Summary

```
Phase 1: Verify Local Setup
  └─ Check all 13 files exist ✅

Phase 2: Docker Build
  └─ docker build -t api-defender . ✅
  └─ docker run api-defender ✅

Phase 3: HF Spaces Setup
  └─ Create account ✅
  └─ Create new Space (Docker runtime) ✅
  └─ Get Space URL ✅

Phase 4: Upload Files
  └─ git clone HF Space ✅
  └─ cp files to Space directory ✅
  └─ git add . && git commit && git push ✅

Phase 5: Wait for Build
  └─ Watch logs (5-10 min) ✅
  └─ Verify "Running" status ✅

Phase 6: Verify Running
  └─ Check green badge ✅
  └─ Test endpoint ✅

Phase 7: Official Validation
  └─ Run validate-submission.sh ✅
  └─ All 3 checks pass ✅

Phase 8: Submit
  └─ Fill hackathon form ✅
  └─ Submit Space URL ✅
```

---

## 🚨 Common Issues & Fixes

### Issue: Docker build fails with "ModuleNotFoundError"
**Fix:** Add missing package to requirements.txt and push again

### Issue: Space stuck on "Building" for 30+ minutes
**Fix:** Cancel and rebuild (Usually means dependency download failed)

### Issue: Space shows "error" badge
**Fix:** Click "Logs" tab to see error, fix, and push again

### Issue: Validation fails on format
**Fix:** Check inference.py produces exactly:
```
[START] task=... env=... model=...
[STEP] step=X action=... reward=... done=... error=...
[END] success=... steps=... score=... rewards=...
```

### Issue: Validation fails on F1 score
**Fix:** Your agent's F1 < 0.70. Check hard_defender_agent.py logic.

### Issue: Can't access Space URL
**Fix:** Ensure Space status is "Running" (green badge)

---

## ✅ Final Checklist

Before final submission:

- [ ] Local Docker build works: `docker build -t api-defender .`
- [ ] Local Docker run works: `docker run api-defender`
- [ ] HF Space URL obtained
- [ ] All files uploaded to Space
- [ ] Space shows "Running" (green badge)
- [ ] Validation script passes all 3 checks
- [ ] Screenshot of passing validation saved
- [ ] Hackathon form filled with Space URL
- [ ] Submitted to hackathon platform

---

## 🎉 Expected Final Output

When everything is working:

**Your Space will:**
1. ✅ Show green "Running" badge
2. ✅ Accept inference requests
3. ✅ Return output in official format
4. ✅ Achieve F1=0.791 (winning score)
5. ✅ Pass all official validation checks

**Example successful output:**
```
[START] task=adversarial-defense env=api-defender model=HardDefender-v1.0
[STEP] step=1 action=block(U42) reward=0.40 done=false error=null
[STEP] step=2 action=block(U88) reward=0.40 done=false error=null
...
[END] success=true steps=25 score=0.791 rewards=0.40,0.40,...,0.40
```

---

## 📞 Quick Reference

| Step | Command | Expected Time |
|------|---------|----------------|
| Docker build | `docker build -t api-defender .` | 2 min |
| Docker test | `docker run api-defender` | <1 min |
| HF Space create | Web UI | <1 min |
| Upload files | `git push` | <1 min |
| Space build | Automatic | 5-10 min |
| Validation | `./validate-submission.sh` | 2 min |
| **Total** | | **20-25 min** |

---

## 🏆 You're Ready!

Your submission is production-ready. Follow these steps and you'll be live in ~20 minutes!

Good luck! 🚀
