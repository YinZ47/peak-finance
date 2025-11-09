# 🚀 Peak Finance - Production Deployment Guide

## 📋 Table of Contents
- [System Requirements](#system-requirements)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Deployment Options](#deployment-options)
- [Security Hardening](#security-hardening)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🔧 System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+), Windows Server 2019+, macOS 10.15+
- **Python**: 3.11 or higher
- **RAM**: 512MB minimum (1GB recommended)
- **Storage**: 500MB minimum
- **Database**: SQLite (dev) or PostgreSQL 12+ (production)

### Recommended Production Specs
- **RAM**: 2GB+
- **CPU**: 2 cores+
- **Storage**: 10GB+ SSD
- **Database**: PostgreSQL 15+
- **Reverse Proxy**: Nginx or Caddy
- **SSL**: Let's Encrypt or commercial certificate

---

## ✅ Pre-Deployment Checklist

### 1. Environment Configuration
```bash
# Copy production environment template
cp .env.production.example .env

# Generate a strong secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Update .env with:
# - SECRET_KEY (generated above)
# - DATABASE_URL (PostgreSQL for production)
# - AI_API_KEY (if using OpenAI)
# - ALLOWED_ORIGINS (your production domain)
```

### 2. Security Requirements
- [ ] Change SECRET_KEY to a random 64-character hex string
- [ ] Set HTTPS-only cookies (secure=True in production)
- [ ] Update CORS ALLOWED_ORIGINS to production domain
- [ ] Review and set appropriate rate limits
- [ ] Enable database backups
- [ ] Set up firewall rules (allow only 80, 443, 22)

### 3. Database Setup
- [ ] For SQLite: Ensure write permissions on app.db
- [ ] For PostgreSQL: Create database and user
- [ ] Run database migrations/initialization
- [ ] Set up automated backups

### 4. Dependencies Check
```bash
# Install all production dependencies
pip install -r requirements.txt

# Verify installations
python -c "import fastapi, uvicorn, sqlalchemy, pydantic; print('✅ Core dependencies OK')"
```

---

## 🌐 Deployment Options

### Option 1: Docker (Recommended)

**Build and Run:**
```bash
# Build Docker image
docker build -t peak-finance:latest .

# Run with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Access at: http://localhost:8000
```

**Production with PostgreSQL:**
```bash
# Uncomment PostgreSQL section in docker-compose.yml
# Update .env with: DATABASE_URL=postgresql://peakuser:changeme@postgres:5432/peakfinance
docker-compose up -d
```

### Option 2: Traditional Server (Ubuntu/Debian)

**1. Install System Dependencies:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nginx certbot python3-certbot-nginx
```

**2. Setup Application:**
```bash
# Create app user
sudo useradd -m -s /bin/bash peakfinance

# Create directory
sudo mkdir -p /var/www/peak-finance
sudo chown peakfinance:peakfinance /var/www/peak-finance

# Switch to app user
sudo su - peakfinance
cd /var/www/peak-finance

# Clone/copy your application
git clone <your-repo> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.production.example .env
nano .env  # Edit configuration
```

**3. Create Systemd Service:**
```bash
sudo nano /etc/systemd/system/peak-finance.service
```

```ini
[Unit]
Description=Peak Finance Web Application
After=network.target

[Service]
Type=notify
User=peakfinance
Group=peakfinance
WorkingDirectory=/var/www/peak-finance
Environment="PATH=/var/www/peak-finance/venv/bin"
ExecStart=/var/www/peak-finance/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**4. Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable peak-finance
sudo systemctl start peak-finance
sudo systemctl status peak-finance
```

**5. Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/peak-finance
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (optional - FastAPI serves them, but Nginx is faster)
    location /static/ {
        alias /var/www/peak-finance/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**6. Enable Site and SSL:**
```bash
sudo ln -s /etc/nginx/sites-available/peak-finance /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Option 3: Platform as a Service (PaaS)

**Heroku:**
```bash
# Install Heroku CLI
# Login: heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-postgres-url

# Deploy
git push heroku main

# Open app
heroku open
```

**Railway / Render / Fly.io:**
- Connect GitHub repository
- Set environment variables via dashboard
- Deploy automatically on push

### Option 4: Windows Server

**1. Install Python 3.11:**
- Download from python.org
- Add to PATH

**2. Setup Application:**
```powershell
# Create directory
mkdir C:\inetpub\peak-finance
cd C:\inetpub\peak-finance

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.production.example .env
notepad .env
```

**3. Run as Windows Service:**
Use NSSM (Non-Sucking Service Manager):
```powershell
# Download NSSM from nssm.cc
nssm install PeakFinance "C:\inetpub\peak-finance\venv\Scripts\python.exe" "C:\inetpub\peak-finance\venv\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000"
nssm start PeakFinance
```

---

## 🔒 Security Hardening

### Application Security

**1. Update main.py for Production:**
```python
# Set secure cookie settings
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=True,  # Enable in production with HTTPS
    samesite="strict",  # CSRF protection
    max_age=86400,
    path="/"
)
```

**2. Rate Limiting (Optional - Add to requirements.txt):**
```bash
pip install slowapi
```

**3. HTTPS Redirect:**
Add to Nginx config:
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

**4. Security Headers:**
Add to Nginx config:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Database Security

**PostgreSQL Setup:**
```sql
-- Create dedicated database and user
CREATE DATABASE peakfinance;
CREATE USER peakuser WITH ENCRYPTED PASSWORD 'strong-password-here';
GRANT ALL PRIVILEGES ON DATABASE peakfinance TO peakuser;

-- Restrict access
-- Edit /etc/postgresql/15/main/pg_hba.conf
-- host    peakfinance    peakuser    127.0.0.1/32    md5
```

**Backup Strategy:**
```bash
# Daily backup cron job
0 2 * * * pg_dump -U peakuser peakfinance > /backups/peak-finance-$(date +\%Y\%m\%d).sql

# Or for SQLite
0 2 * * * cp /var/www/peak-finance/app.db /backups/app-$(date +\%Y\%m\%d).db
```

---

## 📊 Monitoring & Maintenance

### Health Checks

**Endpoint:** `GET /health`
```bash
# Check application health
curl http://localhost:8000/health

# Expected response:
{"status": "healthy", "version": "1.0.0"}
```

### Logging

**View Logs (Systemd):**
```bash
sudo journalctl -u peak-finance -f
```

**View Logs (Docker):**
```bash
docker-compose logs -f web
```

### Monitoring Tools (Optional)

1. **Uptime Monitoring:**
   - UptimeRobot (free)
   - Pingdom
   - StatusCake

2. **Application Performance:**
   - New Relic
   - DataDog
   - Sentry (error tracking)

3. **Server Monitoring:**
   - Prometheus + Grafana
   - Netdata
   - Glances

### Maintenance Tasks

**Weekly:**
- [ ] Review logs for errors
- [ ] Check disk space
- [ ] Verify backups

**Monthly:**
- [ ] Update dependencies: `pip install -U -r requirements.txt`
- [ ] Security audit
- [ ] Performance review

**Quarterly:**
- [ ] Database optimization
- [ ] SSL certificate renewal (automatic with certbot)
- [ ] Disaster recovery test

---

## 🔄 Updates & Rollback

### Update Procedure

**Docker:**
```bash
git pull
docker-compose build
docker-compose up -d
```

**Traditional:**
```bash
sudo su - peakfinance
cd /var/www/peak-finance
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart peak-finance
```

### Rollback

**Docker:**
```bash
docker-compose down
docker run -d peak-finance:previous-tag
```

**Traditional:**
```bash
git revert HEAD
sudo systemctl restart peak-finance
```

---

## 📞 Support & Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check logs
sudo journalctl -u peak-finance -n 50

# Verify Python path
which python3.11

# Test manually
cd /var/www/peak-finance
source venv/bin/activate
python main.py
```

**Database connection errors:**
```bash
# Test PostgreSQL connection
psql -U peakuser -d peakfinance -h localhost

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

**502 Bad Gateway:**
```bash
# Check if app is running
sudo systemctl status peak-finance

# Check Nginx config
sudo nginx -t

# Check firewall
sudo ufw status
```

---

## 📝 Production Checklist

Before going live:
- [ ] All environment variables configured
- [ ] SECRET_KEY is strong and unique
- [ ] HTTPS enabled with valid certificate
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] Firewall configured
- [ ] Security headers enabled
- [ ] Rate limiting enabled
- [ ] Error logging configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Documentation updated

---

**Version:** 1.0.0  
**Last Updated:** November 10, 2025  
**License:** Educational Use Only
