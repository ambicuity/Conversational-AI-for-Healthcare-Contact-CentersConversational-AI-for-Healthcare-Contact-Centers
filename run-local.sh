#!/bin/bash

# Local development script for Healthcare Conversational AI Platform

echo "🏥 Healthcare Conversational AI Platform - Local Development"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp config/.env.example .env
    echo "📝 Please edit .env with your credentials before running"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Set environment for local development
export FLASK_ENV=development
export FLASK_DEBUG=true

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Flask application on http://localhost:8080"
echo ""
echo "Available endpoints:"
echo "  - Health check: http://localhost:8080/health"
echo "  - Metrics: http://localhost:8080/api/v1/metrics"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python app.py
