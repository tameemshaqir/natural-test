# Deployment Guide

Step-by-step instructions to deploy the Cosmetics E-Commerce System.

---

## Option A: Docker Compose (Recommended for Development & Testing)

The fastest way to run the system locally or on a server.

### Prerequisites

- Docker 20+ and Docker Compose v2+
- 2GB+ RAM

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/tameemshaqir/natural-test.git
cd natural-test

# 2. Run setup
bash scripts/setup.sh

# 3. Edit .env with your credentials
nano .env

# 4. Start services
docker compose up -d

# 5. Wait ~30 seconds for initialization, then open:
#    http://localhost:8069
#    Login: admin / admin

# 6. Install the module
bash scripts/install-module.sh

# 7. Verify: Go to Apps → search "Cosmetics Store" → should show as installed
```

### Useful Commands

```bash
docker compose logs -f odoo    # View Odoo logs
docker compose ps              # Check service status
docker compose restart         # Restart services
docker compose down            # Stop services
docker compose down -v         # Stop and delete all data
```

---

## Option B: Manual Installation on Ubuntu Server (Production)

For production deployments on a dedicated Ubuntu server.

### Prerequisites

- Ubuntu 22.04 LTS server
- Minimum 4GB RAM, 2 CPU cores, 50GB storage
- Domain name (e.g., cosmetics-admin.example.com)
- SSL certificate (Let's Encrypt recommended)

---

## Step 1: Prepare Ubuntu Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git wget curl software-properties-common \
  build-essential libssl-dev libffi-dev python3-dev \
  python3-pip python3-venv libxml2-dev libxslt1-dev \
  zlib1g-dev libsasl2-dev libldap2-dev libjpeg-dev \
  libpq-dev node-less npm wkhtmltopdf

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install rtlcss for RTL support (optional)
sudo npm install -g rtlcss
```

## Step 2: Install PostgreSQL

```bash
# Install PostgreSQL 15
sudo apt install -y postgresql postgresql-client

# Create Odoo database user
sudo -u postgres createuser --createdb --no-createrole --no-superuser odoo
sudo -u postgres psql -c "ALTER USER odoo WITH PASSWORD 'your_secure_password';"

# Verify
sudo -u postgres psql -c "SELECT version();"
```

## Step 3: Install Odoo

```bash
# Create Odoo system user
sudo adduser --system --home=/opt/odoo --group odoo

# Clone Odoo 17 Community
sudo git clone --depth 1 --branch 17.0 \
  https://github.com/odoo/odoo.git /opt/odoo/odoo-server

# Install Python dependencies
cd /opt/odoo/odoo-server
sudo pip3 install -r requirements.txt

# Create addons directory
sudo mkdir -p /opt/odoo/custom-addons
sudo chown -R odoo:odoo /opt/odoo
```

## Step 4: Deploy Custom Module

```bash
# Copy the cosmetics_store module
sudo cp -r /path/to/cosmetics_store /opt/odoo/custom-addons/

# Set permissions
sudo chown -R odoo:odoo /opt/odoo/custom-addons/cosmetics_store
```

## Step 5: Configure Odoo

```bash
# Create Odoo config file
sudo tee /etc/odoo.conf << 'EOF'
[options]
admin_passwd = your_admin_master_password
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_secure_password
addons_path = /opt/odoo/odoo-server/addons,/opt/odoo/custom-addons
logfile = /var/log/odoo/odoo.log
log_level = info
xmlrpc_port = 8069
proxy_mode = True
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200
EOF

# Create log directory
sudo mkdir -p /var/log/odoo
sudo chown odoo:odoo /var/log/odoo
```

## Step 6: Create Systemd Service

```bash
sudo tee /etc/systemd/system/odoo.service << 'EOF'
[Unit]
Description=Odoo
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo
PermissionsStartOnly=true
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo-server/odoo-bin -c /etc/odoo.conf
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target
EOF

# Start and enable
sudo systemctl daemon-reload
sudo systemctl start odoo
sudo systemctl enable odoo
sudo systemctl status odoo
```

## Step 7: Install and Enable Module

1. Access Odoo at `http://your-server:8069`
2. Create a new database
3. Go to **Apps** → **Update Apps List**
4. Search for "Cosmetics Store"
5. Click **Install**

## Step 8: Configure Nginx (Reverse Proxy + HTTPS)

```bash
sudo apt install -y nginx certbot python3-certbot-nginx

# Create Nginx config
sudo tee /etc/nginx/sites-available/odoo << 'EOF'
upstream odoo {
    server 127.0.0.1:8069;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_auth:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api_general:10m rate=60r/m;

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Logging
    access_log /var/log/nginx/odoo-access.log;
    error_log /var/log/nginx/odoo-error.log;

    # Proxy
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # API rate limiting
    location /api/v1/auth/ {
        limit_req zone=api_auth burst=10 nodelay;
        proxy_pass http://odoo;
    }

    location /api/v1/ {
        limit_req zone=api_general burst=20 nodelay;
        proxy_pass http://odoo;
    }

    # Odoo backend
    location / {
        proxy_pass http://odoo;
        proxy_read_timeout 720s;
        proxy_connect_timeout 720s;
        proxy_send_timeout 720s;
        client_max_body_size 50m;
    }

    # Static files
    location /web/static/ {
        proxy_cache_valid 200 60m;
        proxy_buffering on;
        expires 24h;
        proxy_pass http://odoo;
    }

    # Gzip
    gzip on;
    gzip_types text/css text/plain application/json application/javascript;
    gzip_min_length 1000;
}
EOF

sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Step 9: Configure System Parameters

In Odoo, go to **Settings** → **Technical** → **System Parameters** and set:

| Key | Value |
|-----|-------|
| `cosmetics_store.api_secret` | Your secure random string (32+ chars) |
| `cosmetics_store.paypal_client_id` | Your PayPal Client ID |
| `cosmetics_store.paypal_secret` | Your PayPal Secret |
| `cosmetics_store.paypal_mode` | sandbox or live |
| `cosmetics_store.firebase_server_key` | Your Firebase Server Key |

## Step 10: Configure PayPal

1. Go to [PayPal Developer](https://developer.paypal.com/)
2. Create a REST API app
3. Get Client ID and Secret
4. Set in Odoo system parameters
5. Test with sandbox credentials first
6. Switch to live when ready

## Step 11: Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Add Android app with your package name
4. Download `google-services.json`
5. Place in `flutter_app/android/app/`
6. Get Server Key from Project Settings → Cloud Messaging
7. Set in Odoo system parameters

## Step 12: Connect Flutter to Backend

Update `flutter_app/lib/core/constants/app_constants.dart`:
```dart
static const String baseUrl = 'https://your-domain.com';
```

## Step 13: Build and Deploy Android APK

```bash
cd flutter_app

# Get dependencies
flutter pub get

# Build release APK
flutter build apk --release

# The APK will be at:
# build/app/outputs/flutter-apk/app-release.apk
```

## Step 14: Server Hardening

```bash
# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Disable root SSH
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Install fail2ban
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Setup automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```
