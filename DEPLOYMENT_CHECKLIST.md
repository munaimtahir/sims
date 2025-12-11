# SIMS Deployment Checklist

This document provides a comprehensive checklist for deploying SIMS to production.

## ✅ Pre-Deployment Checklist

### Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong `SECRET_KEY` (min 50 characters)
- [ ] Configure `ALLOWED_HOSTS` with production domain(s)
- [ ] Set up `DATABASE_URL` for PostgreSQL
- [ ] Configure email backend (SMTP credentials)
- [ ] Set up Redis URL (optional, for caching)

### Database Setup
- [ ] Install PostgreSQL 12+
- [ ] Create production database
- [ ] Create database user with strong password
- [ ] Grant appropriate privileges
- [ ] Test database connection
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`

### Static & Media Files
- [ ] Create media directory: `mkdir -p media`
- [ ] Set proper permissions: `chmod 755 media`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Verify static files location
- [ ] Test file uploads through admin interface

### Dependencies
- [ ] Install Python 3.11+
- [ ] Create virtual environment
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Install system dependencies (PostgreSQL client, etc.)
- [ ] Install Gunicorn
- [ ] Install Nginx

### Security
- [ ] Enable HTTPS (SSL/TLS certificates)
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Configure HSTS headers
- [ ] Review security middleware settings
- [ ] Run security check: `python manage.py check --deploy`

## 🚀 Deployment Steps

### 1. Server Setup (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql nginx git

# Create deployment user
sudo useradd -m -s /bin/bash sims
sudo su - sims

# Create directories
mkdir -p /home/sims/app
mkdir -p /home/sims/logs
```

### 2. Application Deployment

```bash
# Clone repository
cd /home/sims
git clone https://github.com/munaimtahir/sims.git app
cd app

# Create virtual environment
python3.11 -m venv /home/sims/env
source /home/sims/env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
nano .env  # Edit with production values

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### 3. Gunicorn Setup

```bash
# Copy service file
sudo cp deployment/sims.service /etc/systemd/system/

# Edit service file with correct paths
sudo nano /etc/systemd/system/sims.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable sims
sudo systemctl start sims

# Check status
sudo systemctl status sims
```

### 4. Nginx Setup

```bash
# Copy Nginx configuration
sudo cp deployment/nginx_sims.conf /etc/nginx/sites-available/sims

# Edit configuration with your domain
sudo nano /etc/nginx/sites-available/sims

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/sims /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 5. SSL/TLS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## 🧪 Post-Deployment Testing

### Functional Testing
- [ ] Access site via HTTPS
- [ ] Test admin login
- [ ] Test supervisor login
- [ ] Test PG student login
- [ ] Create test rotation
- [ ] Upload test certificate
- [ ] Submit test logbook entry
- [ ] Submit test clinical case
- [ ] Test file uploads
- [ ] Test notifications
- [ ] Test analytics dashboard

### Performance Testing
- [ ] Check page load times
- [ ] Verify static files load correctly
- [ ] Test with multiple concurrent users
- [ ] Monitor server resources (CPU, RAM)
- [ ] Check database connection pooling

### Security Testing
- [ ] Verify HTTPS redirect
- [ ] Check security headers
- [ ] Test CSRF protection
- [ ] Verify session security
- [ ] Test file upload restrictions
- [ ] Review firewall rules

## 📊 Monitoring Setup

### Application Monitoring
- [ ] Set up error tracking (Sentry, optional)
- [ ] Configure application logging
- [ ] Set up log rotation
- [ ] Monitor disk space
- [ ] Monitor database size

### Server Monitoring
- [ ] Set up uptime monitoring
- [ ] Configure CPU/RAM alerts
- [ ] Monitor Nginx access logs
- [ ] Monitor Gunicorn error logs
- [ ] Set up backup monitoring

## 🔄 Maintenance Tasks

### Daily
- [ ] Check application logs
- [ ] Monitor server resources
- [ ] Check backup completion

### Weekly
- [ ] Review error logs
- [ ] Check disk space usage
- [ ] Review security alerts
- [ ] Update dependencies (if needed)

### Monthly
- [ ] Database backup verification
- [ ] Security updates
- [ ] Performance review
- [ ] SSL certificate check

## 🆘 Troubleshooting

### Common Issues

**Service won't start**
```bash
# Check logs
sudo journalctl -u sims -n 50
sudo systemctl status sims

# Check permissions
ls -la /home/sims/app
ls -la /home/sims/app/sims.sock
```

**502 Bad Gateway**
```bash
# Check Gunicorn is running
sudo systemctl status sims

# Check socket file
ls -la /home/sims/app/sims.sock

# Check Nginx error log
sudo tail -f /var/log/nginx/sims_error.log
```

**Static files not loading**
```bash
# Recollect static files
cd /home/sims/app
source /home/sims/env/bin/activate
python manage.py collectstatic --noinput

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

**Database connection errors**
```bash
# Test database connection
sudo -u postgres psql
\c sims_db
\q

# Check PostgreSQL service
sudo systemctl status postgresql

# Verify .env database settings
cat /home/sims/app/.env | grep DATABASE
```

## 📚 Additional Resources

- [POSTGRESQL_SETUP.md](docs/POSTGRESQL_SETUP.md) - PostgreSQL setup guide
- [DEMO_SETUP.md](DEMO_SETUP.md) - Demo setup and walkthrough
- [README.md](README.md) - Project overview
- [deployment/](deployment/) - Deployment configuration files

## ✅ Deployment Verification

Once all steps are complete, verify:

1. ✅ Site accessible via HTTPS
2. ✅ All static files loading
3. ✅ Media uploads working
4. ✅ Database connection stable
5. ✅ Email notifications working (if configured)
6. ✅ Background tasks running (if using Celery)
7. ✅ Logs being written correctly
8. ✅ Backups scheduled and working
9. ✅ Monitoring alerts configured
10. ✅ Security headers in place

---

**Last Updated**: December 2025  
**Version**: 1.0
