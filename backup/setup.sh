#!/bin/bash

# AutoPost Hub - Setup Script for Termux
# This script sets up the AutoPost Hub application on Termux (Android)

set -e

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                     AutoPost Hub - Setup Script                           ║"
echo "║                   Multi-Platform Content Automation                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running on Termux
if [ ! -d "$TERMUX_ANDROID_RUNTIME_ROOT" ] && [ -n "$TERMUX_ANDROID_RUNTIME_ROOT" ]; then
    echo "✓ Termux detected"
else
    echo "⚠ Not running on Termux (this is okay for development)"
fi

echo ""
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 is required. Please install it first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"

echo ""
echo "Step 2: Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Step 3: Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "Step 4: Installing dependencies..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "Step 5: Creating directories..."
mkdir -p instance/uploads
mkdir -p instance/data
echo "✓ Directories created"

echo ""
echo "Step 6: Initializing database..."
python3 << 'EOF'
from app import create_app
from database import init_db

app = create_app()
with app.app_context():
    init_db(app)
    print("✓ Database initialized")
EOF

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                        Setup Complete!                                    ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 To start the application:"
echo "   source venv/bin/activate"
echo "   python3 app.py"
echo ""
echo "🌐 Access the application at:"
echo "   http://localhost:5000"
echo ""
echo "📱 On Termux, to access from other devices:"
echo "   1. Get your Termux IP: ifconfig | grep 'inet '"
echo "   2. Access from other device: http://<TERMUX_IP>:5000"
echo ""
echo "🔐 Default Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  IMPORTANT: Change the default password in production!"
echo ""
echo "🔗 Configuration locations:"
echo "   - App config: config.py"
echo "   - Database: instance/autopost.db"
echo "   - Uploads: instance/uploads/"
echo ""
