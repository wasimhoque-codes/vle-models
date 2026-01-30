#!/bin/bash

# Student Early Warning System - Setup Script
# This script sets up the deployment environment

set -e  # Exit on error

echo "=========================================="
echo "Student Early Warning System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data/processed
mkdir -p data/predictions
mkdir -p models
mkdir -p reports
echo "✓ Directories created"
echo ""

# Check for feature store
if [ -f "data/processed/ews_feature_store.csv" ]; then
    echo "✓ Feature store found"
else
    echo "⚠️  Feature store not found at data/processed/ews_feature_store.csv"
    echo "   Please run your data preparation notebook first"
fi
echo ""

# Check for models
model_count=$(find models -name "*.pkl" 2>/dev/null | wc -l)
if [ "$model_count" -gt 0 ]; then
    echo "✓ Found $model_count trained model(s)"
else
    echo "⚠️  No trained models found"
    echo "   Run: python app/train_models.py"
fi
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Train models (if not done):"
echo "   python app/train_models.py --week 10"
echo ""
echo "2. Generate predictions:"
echo "   python app/batch_predict.py"
echo ""
echo "3. Launch dashboard:"
echo "   streamlit run app/dashboard.py"
echo ""
echo "=========================================="
