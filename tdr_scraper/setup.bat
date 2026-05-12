@echo off
REM TDR Wait Time Scraper Setup Script for Windows

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║  TDR Wait Time Scraper - Setup Script (Windows)           ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Python version
echo ✓ Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)
python --version
echo.

REM Create virtual environment
echo ✓ Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo   Virtual environment created: .\venv
) else (
    echo   Virtual environment already exists: .\venv
)
echo.

REM Activate virtual environment
echo ✓ Activating virtual environment...
call venv\Scripts\activate.bat
echo   Virtual environment activated
echo.

REM Upgrade pip
echo ✓ Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install dependencies
echo ✓ Installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet
echo   Installed: playwright, httpx
echo.

REM Install playwright browsers
echo ✓ Installing Playwright browsers...
playwright install
echo   Playwright setup complete
echo.

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    Setup Complete!                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 次のステップ:
echo   1. 仮想環境を有効化してください:
echo      venv\Scripts\activate.bat
echo.
echo   2. スクレーパーを実行してください:
echo      python scraper.py
echo.
echo   3. 設定をカスタマイズする場合は config.py を編集してください
echo.
echo 詳細はREADME.mdを参照してください。
echo.

pause
