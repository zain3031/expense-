#!/bin/bash

echo "=========================================="
echo " Business Expense Tracker - Streamlit"
echo " Installation Script"
echo "=========================================="
echo ""

# Check Python version
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "[1/3] Creating virtual environment..."
python3 -m venv venv

echo "[2/3] Activating virtual environment..."
source venv/bin/activate

echo "[3/3] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=========================================="
echo " Installation Complete!"
echo "=========================================="
echo ""
echo "To run the application:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the app:"
echo "   streamlit run app.py --server.port 8501"
echo ""
echo "3. Access in browser:"
echo "   http://yourdomain.com:8501"
echo ""
