@echo off
setlocal

cd /D D:\EB_BACKEND

if not exist ".venv" (
    python -m venv .venv
)

call .venv\Scripts\activate

pip install -r requirements.txt

if "%~1"=="test" (
    pip install -r requirements-dev.txt
    pytest -q
    pause
    exit /b
)

if "%~1"=="fmt" (
    pip install -r requirements-dev.txt
    ruff check . --fix
    black .
    pause
    exit /b
)

if "%~1"=="check" (
    pip install -r requirements-dev.txt
    ruff check .
    black . --check
    pause
    exit /b
)

uvicorn app.main:app --reload --port 8000
pause
