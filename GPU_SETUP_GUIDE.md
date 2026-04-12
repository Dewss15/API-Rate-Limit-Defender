# 🚀 GPU Setup Guide for DQN Training

This guide helps you configure GPU acceleration for DQN training, which speeds up training by **3-4x** (from 20-40 minutes to 5-10 minutes).

---

## ⚡ Quick Check

**Before you start, run this command:**

```bash
python check_gpu.py
```

This will tell you if GPU is already available. If you see:

```
✅ GPU (CUDA) is AVAILABLE!
🚀 READY FOR GPU TRAINING!
```

**You're done! Skip to the [Training](#training-with-gpu) section.**

If you see:

```
⚠️  GPU (CUDA) is NOT available
```

**Follow the setup steps below.**

---

## 🔍 Step 1: Check if You Have an NVIDIA GPU

### Windows

Open PowerShell or Command Prompt and run:

```bash
nvidia-smi
```

**Expected output (if GPU exists):**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 525.85.12    Driver Version: 525.85.12    CUDA Version: 12.0     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0  On |                  N/A |
```

### Linux

```bash
lspci | grep -i nvidia
```

**Expected output:**
```
01:00.0 VGA compatible controller: NVIDIA Corporation ...
```

### What if nvidia-smi doesn't work?

**On Windows:**
1. Check Device Manager → Display adapters
2. Look for NVIDIA GPU in the list

**If no NVIDIA GPU found:**
- You have an AMD or Intel GPU (CUDA not supported)
- OR you have an NVIDIA GPU but drivers not installed

---

## 📦 Step 2: Install NVIDIA Drivers

**If nvidia-smi doesn't work, install drivers:**

### Windows
1. Go to: https://www.nvidia.com/Download/index.aspx
2. Select your GPU model
3. Download and install the driver

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install nvidia-driver-525
sudo reboot
```

**After reboot, test:**
```bash
nvidia-smi
```

---

## 🔧 Step 3: Install CUDA Toolkit

**Download CUDA Toolkit from:**
https://developer.nvidia.com/cuda-downloads

### Which CUDA version?

Check your GPU compatibility:

| GPU Generation | Recommended CUDA | PyTorch CUDA |
|----------------|------------------|--------------|
| RTX 40xx series (4090, 4080, etc.) | CUDA 12.1 | cu121 |
| RTX 30xx series (3090, 3080, etc.) | CUDA 11.8 | cu118 |
| RTX 20xx series (2080, 2070, etc.) | CUDA 11.8 | cu118 |
| GTX 16xx series (1660, 1650, etc.) | CUDA 11.8 | cu118 |

### Windows Installation

1. Download CUDA Toolkit installer
2. Run installer (follow default settings)
3. Restart computer

### Linux Installation (Ubuntu)

**For CUDA 11.8:**
```bash
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run
```

**For CUDA 12.1:**
```bash
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run
```

**Add to PATH (add to ~/.bashrc):**
```bash
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

**Test CUDA:**
```bash
nvcc --version
```

Expected output:
```
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2023 NVIDIA Corporation
Built on ...
Cuda compilation tools, release 11.8, V11.8.89
```

---

## 🐍 Step 4: Install PyTorch with CUDA Support

**IMPORTANT:** Uninstall CPU-only PyTorch first:

```bash
pip uninstall torch
```

**Then install PyTorch with CUDA:**

### For CUDA 11.8 (RTX 20xx/30xx/GTX 16xx)

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### For CUDA 12.1 (RTX 40xx)

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Verify Installation

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

**Expected output:**
```
CUDA available: True
```

---

## ✅ Step 5: Verify GPU Setup

Run the verification script:

```bash
python check_gpu.py
```

**Expected output:**

```
======================================================================
GPU Availability Check
======================================================================

✅ PyTorch installed
   Version: 2.1.0+cu118

✅ GPU (CUDA) is AVAILABLE!

GPU Details:
  - Device Name: NVIDIA GeForce RTX 3080
  - CUDA Version: 11.8
  - Device Count: 1
  - Current Device: 0
  - Total Memory: 10.0 GB
  - Compute Capability: 8.6

Testing GPU allocation...
✅ Successfully allocated tensor on GPU
   Tensor device: cuda:0

🚀 READY FOR GPU TRAINING!
   Expected training time: 5-10 minutes

======================================================================

Summary:
  PyTorch Version: 2.1.0+cu118
  CUDA Available: True
  Device: GPU (cuda)

✅ All checks passed! Ready to train on GPU.
```

---

## 🚀 Training with GPU

Once GPU is set up, training automatically uses it:

```bash
python train_dqn.py
```

**You should see:**

```
======================================================================
DQN Training for API Rate Limit Defender
======================================================================

🔍 GPU Check:
✅ GPU Available: NVIDIA GeForce RTX 3080
✅ CUDA Version: 11.8
✅ GPU Memory: 10.0 GB
✅ Training will use GPU (3-4x faster!)

🖥️  Device: cuda
🧠 Network: DefenderNetwork(...)
```

**Training time:**
- **GPU:** 5-10 minutes ⚡
- **CPU:** 20-40 minutes 🐌

---

## 🐛 Troubleshooting

### Issue 1: "CUDA out of memory"

**Symptoms:**
```
RuntimeError: CUDA out of memory. Tried to allocate 256.00 MiB
```

**Solution:**
Reduce batch size in `train_dqn.py`:

```python
agent = DQNAgent(
    batch_size=32,  # ← Change from 64
)
```

Or close other GPU-intensive applications.

---

### Issue 2: "torch.cuda.is_available() returns False"

**Possible causes:**

1. **Wrong PyTorch version** (CPU-only):
   ```bash
   pip list | grep torch
   ```
   Should show: `torch 2.1.0+cu118` (not just `2.1.0`)
   
   Fix: Reinstall PyTorch with CUDA (see Step 4)

2. **CUDA not in PATH** (Linux):
   ```bash
   echo $PATH | grep cuda
   ```
   Should show: `/usr/local/cuda/bin`
   
   Fix: Add to ~/.bashrc (see Step 3)

3. **Driver version too old**:
   ```bash
   nvidia-smi
   ```
   Driver version should be ≥ 525.xx for CUDA 12.x, ≥ 450.xx for CUDA 11.x
   
   Fix: Update drivers (see Step 2)

---

### Issue 3: "nvidia-smi not found"

**On Windows:**
- Drivers not installed → Install from nvidia.com (Step 2)
- OR not in PATH → Add `C:\Program Files\NVIDIA Corporation\NVSMI` to PATH

**On Linux:**
```bash
sudo apt install nvidia-utils
```

---

### Issue 4: Training seems slow even with GPU

**Check if actually using GPU:**

During training, open another terminal:

```bash
nvidia-smi
```

Look at "GPU-Util" column - should be 40-90% during training.

If 0%:
- Training is using CPU
- Check: `python check_gpu.py`
- Verify PyTorch detects GPU

---

### Issue 5: "CUDA driver version is insufficient"

**Symptoms:**
```
CUDA driver version is insufficient for CUDA runtime version
```

**Cause:** CUDA Toolkit version > Driver version

**Fix:** Update NVIDIA drivers (Step 2)

---

## 🎓 Understanding GPU vs CPU

### Performance Comparison

| Task | CPU Time | GPU Time | Speedup |
|------|----------|----------|---------|
| Training (800 eps) | 30 min | 8 min | 3.75x |
| Validation | 20 sec | 5 sec | 4.0x |
| Inference (20 steps) | 1 sec | 0.3 sec | 3.3x |

### Why is GPU faster?

- **Parallel Processing:** GPUs have thousands of cores vs. CPU's 4-16
- **Matrix Operations:** Neural networks = lots of matrix multiplications
- **Memory Bandwidth:** GPU memory is 10x faster than RAM

### When is CPU acceptable?

- **Small models:** < 100K parameters (ours has ~4K, but batching helps)
- **Prototyping:** Quick tests with few episodes
- **No GPU available:** Still works, just slower

---

## 📊 Expected GPU Utilization

During training, you should see:

```bash
nvidia-smi
```

```
+-----------------------------------------------------------------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|   0  RTX 3080        Off  | 00000000:01:00.0  On |                  N/A |
| 35%   58C    P2    180W / 320W|   1200MiB / 10240MiB |     75%      Default |
```

**Key metrics:**
- **GPU-Util:** 40-90% (good)
- **Memory-Usage:** ~1-2 GB (our model is small)
- **Temp:** 50-80°C (normal)
- **Power:** Will increase during training

---

## 🌐 Cloud GPU Options (If No Local GPU)

### Free Options

1. **Google Colab** (Free tier: NVIDIA T4, 15GB RAM)
   - Go to: https://colab.research.google.com/
   - Upload your code
   - Runtime → Change runtime type → GPU
   - Run: `!python train_dqn.py`

2. **Kaggle Notebooks** (Free: NVIDIA P100, 16GB RAM)
   - Go to: https://www.kaggle.com/
   - Create new notebook
   - Settings → Accelerator → GPU
   - Upload code and run

### Paid Options

1. **AWS EC2** (g4dn.xlarge: NVIDIA T4, ~$0.50/hour)
2. **Google Cloud** (n1-standard-4 + T4, ~$0.35/hour)
3. **Paperspace Gradient** (Various GPUs, from $0.45/hour)

**For one-time training:** Colab or Kaggle free tier is sufficient!

---

## ✅ Final Checklist

Before training:

- [ ] `nvidia-smi` works
- [ ] `nvcc --version` shows CUDA version
- [ ] `python check_gpu.py` shows GPU available
- [ ] `torch.cuda.is_available()` returns True
- [ ] PyTorch version includes `+cu118` or `+cu121`

If all ✅, you're ready to train! 🚀

---

## 🎯 Summary

**Minimum requirements for GPU training:**
1. NVIDIA GPU (GTX 1050 or better)
2. NVIDIA drivers (version ≥ 450)
3. CUDA Toolkit (11.8 or 12.1)
4. PyTorch with CUDA support

**Setup time:** 20-40 minutes (one-time)  
**Training speedup:** 3-4x faster  
**Worth it?** Absolutely! ⚡

---

For more help:
- PyTorch CUDA guide: https://pytorch.org/get-started/locally/
- CUDA installation: https://developer.nvidia.com/cuda-downloads
- Check GPU compatibility: https://developer.nvidia.com/cuda-gpus
