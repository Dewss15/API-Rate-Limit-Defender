@echo off
REM Quick verification of HardDefenderAgent on all datasets

echo ================================================================================
echo QUICK VERIFICATION: HardDefenderAgent on data.py
echo ================================================================================
echo.
echo This will test your agent on:
echo   - Easy dataset (10 users)
echo   - Medium dataset (20 users)
echo   - Extreme dataset (40 users)
echo   - Winning dataset (83 users) ⭐ JUDGING METRIC
echo.
echo Press any key to start...
pause > nul
echo.

python verify_hard_agent.py

echo.
pause
