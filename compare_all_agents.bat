@echo off
REM Compare DQN Model vs Rule-Based Agents on Generalization Tests

echo ================================================================================
echo DQN vs RULE-BASED: GENERALIZATION COMPARISON
echo ================================================================================
echo.
echo This will run generalization tests on:
echo   - DQN Model (Machine Learning)
echo   - Easy Rule-Based Agent
echo   - Medium Rule-Based Agent  
echo   - Hard Rule-Based Agent
echo.
echo And provide a side-by-side comparison of:
echo   - Performance on seen vs unseen data
echo   - Generalization gap
echo   - Adversarial robustness
echo   - Premium protection
echo.
echo Press any key to start comprehensive testing...
pause > nul
echo.

echo ================================================================================
echo PART 1: Testing DQN Model
echo ================================================================================
echo.
python test_generalization.py

echo.
echo.
echo ================================================================================
echo PART 2: Testing Rule-Based Agents
echo ================================================================================
echo.
python test_generalization_rulebased.py

echo.
echo ================================================================================
echo TESTING COMPLETE!
echo ================================================================================
echo.
echo Review both outputs above to compare:
echo   - DQN learned patterns vs hardcoded rules
echo   - Which approach generalizes better
echo   - Which is more robust to adversarial examples
echo.
pause
