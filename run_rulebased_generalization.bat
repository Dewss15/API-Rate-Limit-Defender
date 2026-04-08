@echo off
REM Run generalization tests for all RULE-BASED agents
REM Tests Easy, Medium, and Hard defender agents on unseen data

echo ================================================================================
echo RULE-BASED AGENTS GENERALIZATION TESTING SUITE
echo ================================================================================
echo.
echo This will test all 3 rule-based agents on:
echo   1. Synthetic users with RPS outside training range
echo   2. Adversarial examples designed to fool the agents
echo   3. Boundary conditions and edge cases
echo   4. Comparative analysis across all agents
echo.
echo Agents to test:
echo   - EasyDefenderAgent (Simple RPS threshold)
echo   - MediumDefenderAgent (RPS + Suspicious pattern)
echo   - HardDefenderAgent (Risk-based scoring)
echo.
echo Press any key to start testing...
pause > nul
echo.

python test_generalization_rulebased.py

echo.
echo ================================================================================
echo TESTING COMPLETE!
echo ================================================================================
echo.
echo You can compare these results with DQN model results by running:
echo   python test_generalization.py
echo.
pause
