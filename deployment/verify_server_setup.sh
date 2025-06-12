#!/bin/bash
# Server Setup Verification Script for 172.236.152.35
# Run this BEFORE running the deployment script

echo "🔍 SIMS Server Setup Verification for 172.236.152.35"
echo "======================================================="

# Check if we're on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "❌ This script is designed for Ubuntu/Debian systems"
    exit 1
fi

echo "✅ Ubuntu/Debian system detected"

# Check if project directory exists and has correct structure
if [ ! -d "/var/www/sims_project" ]; then
    echo "❌ Project directory /var/www/sims_project not found"
    echo "📋 Please upload your project files first:"
    echo "   scp -r . user@172.236.152.35:/var/www/sims_project/"
    exit 1
fi

echo "✅ Project directory exists"

# Check if manage.py exists
if [ ! -f "/var/www/sims_project/manage.py" ]; then
    echo "❌ Django manage.py not found in project directory"
    echo "📋 Please ensure all Django files are uploaded"
    exit 1
fi

echo "✅ Django project files found"

# Check required files for deployment
required_files=(
    "nginx_sims.conf"
    "gunicorn.conf.py" 
    "sims.service"
    "requirements.txt"
    "deploy_server.sh"
)

for file in "${required_files[@]}"; do
    if [ ! -f "/var/www/sims_project/$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    else
        echo "✅ Found: $file"
    fi
done

# Check if user has sudo access
if ! sudo -n true 2>/dev/null; then
    echo "⚠️  You need sudo access to run the deployment script"
    echo "📋 Make sure your user is in the sudo group"
else
    echo "✅ Sudo access confirmed"
fi

# Check if ports are available
if ss -tulpn | grep -q ":80 "; then
    echo "⚠️  Port 80 is already in use"
    echo "📋 You may need to stop the existing service"
    ss -tulpn | grep ":80 "
else
    echo "✅ Port 80 is available"
fi

echo ""
echo "🎯 VERIFICATION COMPLETE"
echo "======================================="
echo "If all checks passed, you can now run:"
echo "chmod +x deploy_server.sh"
echo "./deploy_server.sh"
echo "======================================="
