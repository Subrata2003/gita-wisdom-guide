@echo off
echo ============================================
echo   Gita Wisdom Guide - React Frontend v2
echo ============================================
echo.
cd /d "%~dp0frontend"

if not exist node_modules (
    echo Installing npm dependencies...
    npm install
    echo.
)

echo Starting frontend on http://localhost:5173
echo.
npm run dev
pause
