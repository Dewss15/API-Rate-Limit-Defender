@echo off
REM Quick GPU check script for Windows
REM Run this before training to verify GPU is available

echo Running GPU check...
echo.

python check_gpu.py

echo.
echo ========================================
echo.
echo If GPU is available, you can now run:
echo   python train_dqn.py
echo.
echo If GPU is NOT available, see GPU_SETUP_GUIDE.md
echo ========================================

pause
