"""
check_gpu.py - Quick GPU availability check for PyTorch

Run this before training to verify GPU is properly configured.
"""

import sys

print("="*70)
print("GPU Availability Check")
print("="*70)
print()

# Check if PyTorch is installed
try:
    import torch
    print("✅ PyTorch installed")
    print(f"   Version: {torch.__version__}")
except ImportError:
    print("❌ PyTorch not installed")
    print("   Install with: pip install torch")
    sys.exit(1)

print()

# Check CUDA availability
if torch.cuda.is_available():
    print("✅ GPU (CUDA) is AVAILABLE!")
    print()
    print("GPU Details:")
    print(f"  - Device Name: {torch.cuda.get_device_name(0)}")
    print(f"  - CUDA Version: {torch.version.cuda}")
    print(f"  - Device Count: {torch.cuda.device_count()}")
    print(f"  - Current Device: {torch.cuda.current_device()}")
    
    # Get memory info
    props = torch.cuda.get_device_properties(0)
    total_memory = props.total_memory / 1024**3
    print(f"  - Total Memory: {total_memory:.1f} GB")
    print(f"  - Compute Capability: {props.major}.{props.minor}")
    
    # Test GPU allocation
    print()
    print("Testing GPU allocation...")
    try:
        test_tensor = torch.randn(1000, 1000).cuda()
        print("✅ Successfully allocated tensor on GPU")
        print(f"   Tensor device: {test_tensor.device}")
        del test_tensor
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"❌ Error allocating tensor: {e}")
    
    print()
    print("🚀 READY FOR GPU TRAINING!")
    print("   Expected training time: 5-10 minutes")
    
else:
    print("⚠️  GPU (CUDA) is NOT available")
    print()
    print("Possible reasons:")
    print("  1. No NVIDIA GPU in your system")
    print("  2. CUDA not installed")
    print("  3. PyTorch CPU-only version installed")
    print()
    print("To enable GPU support:")
    print()
    print("Step 1: Check if you have an NVIDIA GPU")
    print("  - Windows: nvidia-smi")
    print("  - Linux: lspci | grep -i nvidia")
    print()
    print("Step 2: Install CUDA Toolkit")
    print("  - Download from: https://developer.nvidia.com/cuda-downloads")
    print()
    print("Step 3: Install PyTorch with CUDA support")
    print("  - For CUDA 11.8:")
    print("    pip install torch --index-url https://download.pytorch.org/whl/cu118")
    print("  - For CUDA 12.1:")
    print("    pip install torch --index-url https://download.pytorch.org/whl/cu121")
    print()
    print("⚠️  Training will use CPU")
    print("   Expected training time: 20-40 minutes")

print()
print("="*70)

# Summary
print()
print("Summary:")
print(f"  PyTorch Version: {torch.__version__}")
print(f"  CUDA Available: {torch.cuda.is_available()}")
print(f"  Device: {'GPU (cuda)' if torch.cuda.is_available() else 'CPU'}")

if torch.cuda.is_available():
    print()
    print("✅ All checks passed! Ready to train on GPU.")
else:
    print()
    print("ℹ️  Training will work on CPU, but will be slower.")
    print("   For GPU training, follow the steps above.")
