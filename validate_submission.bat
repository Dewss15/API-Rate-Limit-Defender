@echo off
REM validate_submission.bat - Run validation tests on submission files
echo.
echo ========================================
echo Running Submission Validation...
echo ========================================
echo.

python validate_submission.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Validation failed! Please fix errors above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Validation Complete!
echo ========================================
pause
