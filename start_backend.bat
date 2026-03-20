@echo off
echo ============================================
echo   Gita Wisdom Guide - FastAPI Backend v2
echo ============================================
echo.
echo Starting backend on http://localhost:8000
echo API docs at   http://localhost:8000/docs
echo.
cd /d "%~dp0"
C:\Users\subra\anaconda3\python.exe -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
pause
