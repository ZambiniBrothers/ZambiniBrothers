#!/bin/bash

# TDR Wait Time Scraper Setup Script
# This script sets up the environment and installs all dependencies

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║  TDR Wait Time Scraper - Setup Script                     ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $python_version"

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Virtual environment created: ./venv"
else
    echo "  Virtual environment already exists: ./venv"
fi

# Activate virtual environment
echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate
echo "  Virtual environment activated"

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "✓ Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet
echo "  Installed: playwright, httpx"

# Install playwright browsers
echo ""
echo "✓ Installing Playwright browsers..."
playwright install
echo "  Playwright setup complete"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "次のステップ:"
echo "  1. 仮想環境を有効化してください:"
echo "     source venv/bin/activate"
echo ""
echo "  2. スクレーパーを実行してください:"
echo "     python scraper.py"
echo ""
echo "  3. 設定をカスタマイズする場合は config.py を編集してください"
echo ""
echo "詳細はREADME.mdを参照してください。"
echo ""
