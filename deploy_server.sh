#!/bin/bash
# SIMS Deployment Script for Nginx Server 172.236.152.35
# Run this script on your server to deploy the SIMS project

echo "🚀 SIMS Deployment Script for Nginx Server 172.236.152.35"
echo "=========================================================="

# Set working directory
cd /var/www/sims_project

echo "📁 Setting up directories..."
# Create necessary directories
mkdir -p static
mkdir -p staticfiles  
mkdir -p media
mkdir -p logs
mkdir -p backups

echo "🔐 Setting environment variables..."
# Set environment variables for production
export SECRET_KEY="$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
export DEBUG="False"
export ALLOWED_HOSTS="172.236.152.35,localhost,127.0.0.1"

echo "📦 Installing dependencies..."
# Activate virtual environment and install requirements
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # Install Gunicorn for Nginx

echo "🗄️ Setting up database..."
# Run migrations
python manage.py migrate

echo "📁 Collecting static files..."
# Collect static files
python manage.py collectstatic --noinput

echo "👤 Creating superuser..."
# Create superuser (interactive)
echo "Please create an admin user for the system:"
python manage.py createsuperuser

echo "🔧 Setting file permissions..."
# Set proper permissions
sudo chown -R www-data:www-data /var/www/sims_project
sudo chmod -R 755 /var/www/sims_project
sudo chmod -R 775 /var/www/sims_project/media
sudo chmod -R 775 /var/www/sims_project/logs
sudo chmod 664 /var/www/sims_project/db.sqlite3

echo "⚙️ Setting up Nginx and Gunicorn..."
# Copy Nginx configuration
sudo cp nginx_sims.conf /etc/nginx/sites-available/sims
sudo ln -sf /etc/nginx/sites-available/sims /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Remove default site

# Copy systemd service file
sudo cp sims.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sims

echo "🧪 Testing configuration..."
# Test Nginx configuration
sudo nginx -t

# Test that Django can start
python manage.py check --deploy

echo "🚀 Starting services..."
# Start SIMS service
sudo systemctl start sims

# Restart Nginx
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your SIMS system at:"
echo "   Homepage: http://172.236.152.35/"
echo "   Login:    http://172.236.152.35/users/login/"
echo "   Admin:    http://172.236.152.35/admin/"
echo ""
echo "🔧 Service management commands:"
echo "   sudo systemctl status sims     # Check SIMS status"
echo "   sudo systemctl restart sims    # Restart SIMS"
echo "   sudo systemctl status nginx    # Check Nginx status"
echo "   sudo systemctl restart nginx   # Restart Nginx"
echo ""
echo "📋 Next steps:"
echo "   1. Test all functionality"
echo "   2. Set up SSL certificates (recommended)"
echo "   3. Configure firewall rules"
echo "   4. Set up automated backups"
