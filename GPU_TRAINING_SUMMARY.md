# ⚡ GPU Training - Complete Setup

**Quick guide to ensure your DQN training uses GPU acceleration**

---

## 🎯 Goal

Train the DQN model **3-4x faster** using GPU instead of CPU.

| Method | Time | Speed |
|--------|------|-------|
| **GPU (CUDA)** | **5-10 min** | **⚡⚡⚡⚡** |
| CPU | 20-40 min | 🐌 |

---

## ⚡ Quick Start

### Step 1: Check GPU Status

**Run this command:**

```bash
python check_gpu.py
```

Or on Windows, double-click:
```
check_gpu.bat
```

---

### Step 2: Interpret Results

#### ✅ **If you see this - YOU'RE READY!**

```
✅ GPU (CUDA) is AVAILABLE!
✅ GPU Available: NVIDIA GeForce RTX 3080
✅ CUDA Version: 11.8
🚀 READY FOR GPU TRAINING!
```

**→ Skip to [Step 3: Train](#step-3-train-with-gpu)**

---

#### ⚠️ **If you see this - SETUP NEEDED**

```
⚠️  GPU (CUDA) is NOT available
⚠️  Training will use CPU
⚠️  This will take 20-40 minutes instead of 5-10 minutes
```

**→ Follow the [GPU Setup Guide](#gpu-setup-quick-version)**

---

## 🚀 Step 3: Train with GPU

Once GPU is verified, simply run:

```bash
python train_dqn.py
```

**You should see this at the start:**

```
🔍 GPU Check:
✅ GPU Available: NVIDIA GeForce RTX 3080
✅ CUDA Version: 11.8
✅ GPU Memory: 10.0 GB
✅ Training will use GPU (3-4x faster!)

🖥️  Device: cuda
```

**If you see `Device: cpu` instead of `Device: cuda`:**
- GPU is not properly configured
- Re-run `python check_gpu.py`
- Follow troubleshooting steps below

---

## 🔧 GPU Setup (Quick Version)

### Requirements

1. **NVIDIA GPU** (GTX 1050 or newer)
2. **NVIDIA Drivers** (version ≥ 450)
3. **CUDA Toolkit** (11.8 or 12.1)
4. **PyTorch with CUDA**

### Quick Install (Windows)

1. **Check if you have NVIDIA GPU:**
   ```bash
   nvidia-smi
   ```
   
   If this works, skip to Step 3.

2. **Install NVIDIA Drivers:**
   - Go to: https://www.nvidia.com/Download/index.aspx
   - Download and install latest driver
   - Restart computer

3. **Install PyTorch with CUDA:**
   
   Uninstall CPU version first:
   ```bash
   pip uninstall torch
   ```
   
   Install GPU version (CUDA 11.8):
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```
   
   Or for newer GPUs (CUDA 12.1):
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Verify:**
   ```bash
   python check_gpu.py
   ```

**For detailed instructions:** See `GPU_SETUP_GUIDE.md`

---

## 🐛 Troubleshooting

### Issue 1: Training uses CPU even though GPU exists

**Check:**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

**If False:**
- You have CPU-only PyTorch
- Reinstall: `pip install torch --index-url https://download.pytorch.org/whl/cu118`

**Verify PyTorch version:**
```bash
pip show torch
```

Should show: `Version: 2.1.0+cu118` (note the `+cu118`)  
NOT: `Version: 2.1.0` (this is CPU-only)

---

### Issue 2: nvidia-smi not found

**Means:** NVIDIA drivers not installed

**Fix:**
1. Download from: https://www.nvidia.com/Download/index.aspx
2. Install and restart

---

### Issue 3: CUDA out of memory

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Fix:** Reduce batch size in `train_dqn.py`:
```python
agent = DQNAgent(
    batch_size=32,  # was 64
)
```

---

### Issue 4: "CUDA driver version insufficient"

**Means:** Driver too old for CUDA version

**Fix:** Update NVIDIA drivers (see Issue 2)

---

## 📊 How to Verify GPU is Being Used

### During Training

**Open a second terminal and run:**
```bash
nvidia-smi
```

**You should see:**
```
+-----------------------------------------------------------------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|   0  RTX 3080        Off  | 00000000:01:00.0  On |                  N/A |
| 35%   58C    P2    180W / 320W|   1200MiB / 10240MiB |     75%      Default |
```

**Key indicators:**
- **GPU-Util:** Should be 40-90% during training ✅
- **Memory-Usage:** ~1-2 GB used ✅
- **Temp:** Will increase (50-80°C is normal) ✅

**If GPU-Util is 0%:**
- Training is using CPU, not GPU
- Check: `python check_gpu.py`

---

## 🌐 No GPU? Use Cloud

### Free Options

**1. Google Colab (Recommended)**
- Free GPU: NVIDIA T4
- 15GB RAM
- No setup needed

Steps:
1. Go to: https://colab.research.google.com/
2. Upload `train_dqn.py`, `environment.py`, `models.py`, `data.py`, `grader.py`
3. Runtime → Change runtime type → GPU
4. Run: `!python train_dqn.py`

**2. Kaggle Notebooks**
- Free GPU: NVIDIA P100
- 16GB RAM

Steps:
1. Go to: https://www.kaggle.com/
2. Create new notebook
3. Settings → Accelerator → GPU
4. Upload files and run

---

## 📁 Files Created

| File | Purpose |
|------|---------|
| `check_gpu.py` | GPU availability checker |
| `check_gpu.bat` | Windows shortcut for GPU check |
| `GPU_SETUP_GUIDE.md` | Detailed GPU setup instructions |
| `GPU_TRAINING_SUMMARY.md` | This file |

---

## ✅ Pre-Training Checklist

Before running `python train_dqn.py`:

- [ ] Run `python check_gpu.py`
- [ ] See "✅ GPU (CUDA) is AVAILABLE!"
- [ ] `torch.cuda.is_available()` returns True
- [ ] `nvidia-smi` shows your GPU
- [ ] PyTorch version includes `+cu118` or `+cu121`

**If all ✅:** You're ready for **5-10 minute** GPU training! 🚀

**If any ❌:** Follow [GPU Setup](#gpu-setup-quick-version)

---

## 🎓 Why GPU Matters

### Performance Impact

Our DQN training:
- **800 episodes**
- **~16,000 steps total**
- **~1 million neural network forward passes**

**Each forward pass:**
- CPU: ~50 microseconds
- GPU: ~15 microseconds

**Total time saved:** 30-40 minutes → 5-10 minutes

### When is CPU Okay?

- **Quick testing** (50 episodes instead of 800)
- **No GPU available** (works, just slower)
- **Initial development** (prototype with fewer episodes)

**For production training:** GPU is highly recommended!

---

## 🚀 Quick Reference

```bash
# 1. Check GPU
python check_gpu.py

# 2. If GPU available
python train_dqn.py          # Trains in 5-10 min

# 3. Verify (after training)
python test_pt_model.py      # Tests trained model

# 4. Monitor during training (separate terminal)
nvidia-smi                    # Check GPU usage
```

---

## 💡 Pro Tips

1. **Close other GPU apps** before training (Chrome, games, video players)
2. **Monitor GPU temp** with `nvidia-smi` - should stay < 85°C
3. **Use GPU for inference too** - `test_pt_model.py` also benefits
4. **Multiple GPUs?** PyTorch uses GPU 0 by default (usually fastest)

---

## 📞 Need Help?

1. **GPU not detected:** See `GPU_SETUP_GUIDE.md` - detailed troubleshooting
2. **Installation issues:** Check PyTorch docs: https://pytorch.org/get-started/
3. **Out of memory:** Reduce batch_size in `train_dqn.py`
4. **Still stuck:** Use Google Colab (free, no setup)

---

**Bottom Line:** GPU makes training **3-4x faster**. Worth the 20-minute setup!

🚀 Happy Training!
