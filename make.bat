@echo off

if "%1" == "format" (
    echo python -m black --line-length 120 --target-version py38 .
    python -m black --line-length 120 --target-version py38 .
    exit /B %ERRORLEVEL%
) else if "%1" == "checkstyle" (
    echo python -m black --line-length 120 --target-version py38 --check .
    python -m black --line-length 120 --target-version py38 --check .
    exit /B %ERRORLEVEL%
)

echo Usage:
echo   make ^<command^>
echo.
echo Commands:
echo   format                       Format all .py files in this directory.
echo   checkstyle                   Check which .py files in this directory need reformatting.
