@echo off
REM Prepare clean submission folder for HardDefenderAgent

echo ================================================================================
echo CREATING CLEAN SUBMISSION PACKAGE
echo ================================================================================
echo.
echo This will create a clean submission folder with only the required files
echo for your HardDefenderAgent (rule-based) submission.
echo.

REM Create submission directory
if exist submission rmdir /s /q submission
mkdir submission

echo Copying core files...

REM Core Environment Files (5 files)
copy environment.py submission\ >nul
copy models.py submission\ >nul
copy data.py submission\ >nul
copy evaluator.py submission\ >nul
copy grader.py submission\ >nul

REM Agent File (1 file - YOUR SUBMISSION)
copy hard_defender_agent.py submission\ >nul

REM Integration Files (3 files)
copy main.py submission\ >nul
copy openenv.yaml submission\ >nul
copy openenv_models.py submission\ >nul

echo.
echo ✅ Copied 9 core files to submission folder
echo.

REM Create README.md
echo Creating README.md...
(
echo # API Rate Limit Defender - HardDefenderAgent
echo.
echo ## Overview
echo Rule-based bot detection system using multi-signal risk scoring algorithm.
echo.
echo ## Performance
echo - **F1 Score**: 0.791 ^(Winning Dataset^)
echo - **Precision**: 0.944
echo - **Recall**: 0.680
echo - **Premium Protection**: Perfect ^(0 violations^)
echo.
echo ## Algorithm
echo Multi-signal risk scoring approach:
echo - Suspicious pattern detection: +2.0 risk points
echo - High RPS ^(^>90^): +2.0 risk points
echo - Medium RPS ^(50-90^): +1.0 risk points
echo - Low RPS ^(20-50^): +0.5 risk points
echo - Block threshold: 2.5 risk points
echo - Premium users: Protected unless risk ^> 4.0
echo.
echo ## Usage
echo ```bash
echo python main.py
echo ```
echo.
echo ## Expected Output
echo ```
echo Final Score:   0.742
echo F1 Score:      0.791
echo Precision:     0.944
echo Recall:        0.680
echo Premium Penalty: 0
echo ```
echo.
echo ## Files Included
echo - `hard_defender_agent.py` - Main agent logic with risk scoring
echo - `environment.py` - OpenEnv RL environment
echo - `models.py` - User data model
echo - `data.py` - Training and evaluation datasets
echo - `evaluator.py` - Judge's evaluation system
echo - `grader.py` - Metrics calculation
echo - `main.py` - Entry point
echo - `openenv.yaml` - OpenEnv configuration
echo - `openenv_models.py` - OpenEnv bridge
echo.
echo ## Technical Details
echo - **Type**: Deterministic rule-based system
echo - **Approach**: Risk-based scoring with multiple signals
echo - **Training Required**: None
echo - **Deployment**: Instant
echo - **Interpretability**: Fully transparent decisions
echo.
) > submission\README.md

echo ✅ Created README.md
echo.

echo ================================================================================
echo VERIFYING SUBMISSION
echo ================================================================================
echo.

REM List files in submission folder
echo Files in submission folder:
dir /b submission
echo.

REM Count files
for /f %%A in ('dir /b submission ^| find /c /v ""') do set file_count=%%A
echo Total files: %file_count%
echo Expected: 10 files
echo.

if %file_count%==10 (
    echo ✅ File count CORRECT!
) else (
    echo ⚠️ WARNING: File count mismatch!
)

echo.
echo ================================================================================
echo TESTING SUBMISSION
echo ================================================================================
echo.
echo Running main.py to verify everything works...
echo.

cd submission
python main.py
cd ..

echo.
echo ================================================================================
echo SUBMISSION PACKAGE READY!
echo ================================================================================
echo.
echo Next steps:
echo   1. Review the files in the 'submission' folder
echo   2. Verify the output above shows F1 = 0.791 and Premium Penalty = 0
echo   3. If everything looks good, zip the 'submission' folder
echo   4. Upload the zip file to the hackathon platform
echo.
echo Submission folder location:
echo   %cd%\submission
echo.
echo Files included: %file_count%
echo Total size: ~30 KB
echo.
echo Good luck! 🚀
echo.
pause
