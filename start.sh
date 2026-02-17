#!/bin/bash
# Quick Start Script for MedAssist Knowledge Graph

echo "======================================"
echo "MedAssist Knowledge Graph Quick Start"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q neo4j python-dotenv colorama google-generativeai langchain langchain-google-genai

echo ""
echo "✓ Setup complete!"
echo ""
echo "Available commands:"
echo "  1. Initialize database:  python ingest.py"
echo "  2. Run test queries:     python test_queries.py"
echo "  3. Interactive app:      python main.py"
echo ""
echo "Choose an option:"
echo "  [1] Initialize database (setup + ingest data)"
echo "  [2] Run test queries"
echo "  [3] Launch interactive app"
echo "  [4] Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "Initializing database..."
        python ingest.py
        ;;
    2)
        echo ""
        echo "Running test queries..."
        python test_queries.py
        ;;
    3)
        echo ""
        echo "Launching interactive app..."
        python main.py
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
