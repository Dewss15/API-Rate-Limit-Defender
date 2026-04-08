@echo off
REM Run comprehensive generalization testing suite
REM Tests the DQN model on out-of-distribution data

echo ================================================================================
echo DQN MODEL GENERALIZATION TESTING SUITE
echo ================================================================================
echo.
echo This will test your model on:
echo   1. Synthetic users with RPS outside training range
echo   2. Adversarial examples designed to fool the model
echo   3. Boundary conditions and edge cases
echo   4. RPS range sensitivity analysis
echo.
echo Press any key to start testing...
pause > nul
echo.

python test_generalization.py

echo.
echo ================================================================================
echo TESTING COMPLETE!
echo ================================================================================
echo.
pause
