# Omeka S Quick Reference Guide

This guide provides quick commands and patterns for common Omeka S tasks, covering both Docker-based and traditional server installations.

---

## INSTALLATION DETECTION

First, determine what type of installation you're working with:

```bash
# Check if Docker containers are running
docker ps | grep omeka
# If this returns results, it's Docker-based

# Check for traditional installation
ls /var/www/html/omeka-s  # or wherever Omeka is installed
# If path exists and contains Omeka files, it's traditional
```

---

## COMMAND PATTERNS

### Docker-Based Installation

```bash
# Container names (adjust if different)
APP_CONTAINER="omeka-s-app"
DB_CONTAINER="omeka-s-db"

# Base path inside container
OMEKA_PATH="/var/www/html"

# Read file
docker exec $APP_CONTAINER cat $OMEKA_PATH/{path}/file.ext

# List directory
docker exec $APP_CONTAINER ls -la $OMEKA_PATH/{path}/

# Copy file TO container
docker cp local-file.ext $APP_CONTAINER:$OMEKA_PATH/{path}/

# Copy file FROM container
docker cp $APP_CONTAINER:$OMEKA_PATH/{path}/file.ext ./

# Fix permissions after copying
docker exec $APP_CONTAINER chown -R www-data:www-data $OMEKA_PATH/{path}

# Execute PHP command
docker exec $APP_CONTAINER php -r "php code here"

# Database access
docker exec -i $DB_CONTAINER mariadb -u user -ppassword dbname
```

### Traditional Server Installation

```bash
# Base path (adjust to your installation)
OMEKA_PATH="/var/www/html/omeka-s"

# Read file
cat $OMEKA_PATH/{path}/file.ext

# List directory
ls -la $OMEKA_PATH/{path}/

# Copy/edit files directly
cp source.ext $OMEKA_PATH/{path}/
nano $OMEKA_PATH/{path}/file.ext

# Fix permissions
sudo chown -R www-data:www-data $OMEKA_PATH/{path}
sudo chmod -R 755 $OMEKA_PATH/{path}

# Execute PHP command
php -r "php code here"

# Database access
mysql -u user -p dbname
```

---

## FILE LOCATIONS (Same for Both)

Relative to Omeka root directory:

| Purpose | Path |
|---------|------|
| Themes | `/themes/` |
| Modules | `/modules/` |
| Configuration | `/config/` |
| Database config | `/config/database.ini` |
| Local config | `/config/local.config.php` |
| Uploaded files | `/files/` or `/volume/files/` |
| Application logs | `/logs/application.log` |
| Core application | `/application/` |
| Default templates | `/application/view/omeka/site/` |
| Vendor libraries | `/vendor/` |

---

## THEME OPERATIONS

### Read Theme Files

**Docker:**
```bash
docker exec omeka-s-app cat /var/www/html/themes/default/config/theme.ini
docker exec omeka-s-app ls -la /var/www/html/themes/default/asset/css/
```

**Traditional:**
```bash
cat /var/www/html/omeka-s/themes/default/config/theme.ini
ls -la /var/www/html/omeka-s/themes/default/asset/css/
```

### Modify CSS

**Docker:**
```bash
# Download
docker cp omeka-s-app:/var/www/html/themes/default/asset/css/style.css ./

# Edit locally, then upload
docker cp style.css omeka-s-app:/var/www/html/themes/default/asset/css/

# Fix permissions
docker exec omeka-s-app chown www-data:www-data /var/www/html/themes/default/asset/css/style.css
```

**Traditional:**
```bash
# Edit directly
sudo nano /var/www/html/omeka-s/themes/default/asset/css/style.css

# Or use local editor with SFTP/SCP
scp style.css user@server:/var/www/html/omeka-s/themes/default/asset/css/
```

### Install New Theme

**Docker:**
```bash
# Upload theme directory
docker cp my-theme omeka-s-app:/var/www/html/themes/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/themes/my-theme
```

**Traditional:**
```bash
# Copy or extract theme
sudo cp -r my-theme /var/www/html/omeka-s/themes/
sudo chown -R www-data:www-data /var/www/html/omeka-s/themes/my-theme
sudo chmod -R 755 /var/www/html/omeka-s/themes/my-theme
```

---

## MODULE OPERATIONS

### List Installed Modules

**Docker:**
```bash
docker exec omeka-s-app ls /var/www/html/modules/
```

**Traditional:**
```bash
ls /var/www/html/omeka-s/modules/
```

### Install New Module

**Docker:**
```bash
docker cp MyModule omeka-s-app:/var/www/html/modules/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/MyModule
```

**Traditional:**
```bash
sudo cp -r MyModule /var/www/html/omeka-s/modules/
sudo chown -R www-data:www-data /var/www/html/omeka-s/modules/MyModule
sudo chmod -R 755 /var/www/html/omeka-s/modules/MyModule
```

### Edit Module Files

**Docker:**
```bash
# Download
docker cp omeka-s-app:/var/www/html/modules/MyModule ./

# Edit locally, then upload
docker cp MyModule omeka-s-app:/var/www/html/modules/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/MyModule
```

**Traditional:**
```bash
# Edit directly on server
sudo nano /var/www/html/omeka-s/modules/MyModule/Module.php

# Or use SFTP/SCP
scp -r MyModule user@server:/var/www/html/omeka-s/modules/
```

---

## CONFIGURATION

### Check Database Configuration

**Docker:**
```bash
docker exec omeka-s-app cat /var/www/html/config/database.ini
```

**Traditional:**
```bash
cat /var/www/html/omeka-s/config/database.ini
```

### Edit Local Configuration

**Docker:**
```bash
# Download
docker cp omeka-s-app:/var/www/html/config/local.config.php ./

# Edit, then upload
docker cp local.config.php omeka-s-app:/var/www/html/config/
docker exec omeka-s-app chown www-data:www-data /var/www/html/config/local.config.php
```

**Traditional:**
```bash
sudo nano /var/www/html/omeka-s/config/local.config.php
```

### Check Omeka Version

**Docker:**
```bash
docker exec omeka-s-app cat /var/www/html/application/Module.php | grep VERSION
```

**Traditional:**
```bash
cat /var/www/html/omeka-s/application/Module.php | grep VERSION
```

---

## DEBUGGING & LOGS

### View Application Logs

**Docker:**
```bash
docker exec omeka-s-app cat /var/www/html/logs/application.log
docker exec omeka-s-app tail -f /var/www/html/logs/application.log  # Follow
```

**Traditional:**
```bash
cat /var/www/html/omeka-s/logs/application.log
tail -f /var/www/html/omeka-s/logs/application.log  # Follow
```

### View Container/Server Logs

**Docker:**
```bash
docker logs omeka-s-app --tail=50
docker logs omeka-s-app -f  # Follow
docker logs omeka-s-db --tail=50  # Database logs
```

**Traditional:**
```bash
# Apache logs
sudo tail -f /var/log/apache2/error.log
sudo tail -f /var/log/apache2/access.log

# Nginx logs (if using nginx)
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# PHP-FPM logs
sudo tail -f /var/log/php8.1-fpm.log
```

### Check PHP Syntax

**Docker:**
```bash
docker exec omeka-s-app php -l /var/www/html/modules/MyModule/Module.php
```

**Traditional:**
```bash
php -l /var/www/html/omeka-s/modules/MyModule/Module.php
```

### Clear Cache

**Docker:**
```bash
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*
docker compose restart omeka-s
```

**Traditional:**
```bash
sudo rm -rf /var/www/html/omeka-s/application/data/cache/*
sudo systemctl restart apache2  # or nginx
sudo systemctl restart php8.1-fpm  # if using PHP-FPM
```

---

## DATABASE OPERATIONS

### Database Backup

**Docker:**
```bash
docker exec omeka-s-db mariadb-dump -u omekas -pomekas omekas > backup.sql
# Or with mysqldump
docker exec omeka-s-db mysqldump -u omekas -pomekas omekas > backup.sql
```

**Traditional:**
```bash
mysqldump -u omeka_user -p omeka_db > backup.sql
```

### Database Restore

**Docker:**
```bash
docker exec -i omeka-s-db mariadb -u omekas -pomekas omekas < backup.sql
```

**Traditional:**
```bash
mysql -u omeka_user -p omeka_db < backup.sql
```

### Access Database Console

**Docker:**
```bash
docker exec -it omeka-s-db mariadb -u omekas -pomekas omekas
# Or MySQL
docker exec -it omeka-s-db mysql -u omekas -pomekas omekas
```

**Traditional:**
```bash
mysql -u omeka_user -p omeka_db
```

### Common SQL Queries

```sql
-- List all sites
SELECT id, slug, title FROM site;

-- List all items
SELECT id, title FROM resource WHERE resource_type = 'Omeka\Entity\Item' LIMIT 10;

-- Change site theme
UPDATE site_setting SET value = 's:7:"default";' WHERE id = 'theme' AND site_id = 1;

-- List installed modules
SELECT id, is_active FROM module;

-- Get user list
SELECT id, email, role FROM user;
```

---

## FILE PERMISSIONS

### Check Permissions

**Docker:**
```bash
docker exec omeka-s-app ls -la /var/www/html/modules/
docker exec omeka-s-app ls -la /var/www/html/themes/
docker exec omeka-s-app ls -la /var/www/html/files/
```

**Traditional:**
```bash
ls -la /var/www/html/omeka-s/modules/
ls -la /var/www/html/omeka-s/themes/
ls -la /var/www/html/omeka-s/files/
```

### Fix Permissions

**Docker:**
```bash
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/
docker exec omeka-s-app chmod -R 755 /var/www/html/themes/
docker exec omeka-s-app chmod -R 755 /var/www/html/modules/
docker exec omeka-s-app chmod -R 775 /var/www/html/files/
```

**Traditional:**
```bash
sudo chown -R www-data:www-data /var/www/html/omeka-s/
sudo chmod -R 755 /var/www/html/omeka-s/themes/
sudo chmod -R 755 /var/www/html/omeka-s/modules/
sudo chmod -R 775 /var/www/html/omeka-s/files/
```

---

## SERVICE MANAGEMENT

### Restart Services

**Docker:**
```bash
# Restart Omeka container
docker restart omeka-s-app

# Restart all containers
docker compose restart

# Stop containers
docker compose down

# Start containers
docker compose up -d

# View container status
docker compose ps
```

**Traditional:**
```bash
# Apache
sudo systemctl restart apache2
sudo systemctl status apache2

# Nginx
sudo systemctl restart nginx
sudo systemctl status nginx

# PHP-FPM
sudo systemctl restart php8.1-fpm
sudo systemctl status php8.1-fpm

# MySQL/MariaDB
sudo systemctl restart mysql  # or mariadb
sudo systemctl status mysql
```

---

## ENVIRONMENT DETECTION IN SCRIPTS

If creating automation scripts that need to work with both:

```bash
#!/bin/bash

# Detect environment
if docker ps 2>/dev/null | grep -q omeka; then
    ENVIRONMENT="docker"
    OMEKA_PATH="/var/www/html"
    echo "Detected Docker environment"
else
    ENVIRONMENT="traditional"
    OMEKA_PATH="/var/www/html/omeka-s"  # Adjust as needed
    echo "Detected traditional installation"
fi

# Function to execute commands based on environment
run_command() {
    if [ "$ENVIRONMENT" = "docker" ]; then
        docker exec omeka-s-app "$@"
    else
        "$@"
    fi
}

# Example usage
run_command cat "$OMEKA_PATH/config/database.ini"
run_command ls -la "$OMEKA_PATH/themes/"
```

---

## COMMON ISSUES & SOLUTIONS

### Theme/Module Not Appearing

**Check:**
1. File permissions (should be readable by web server)
2. theme.ini or module.ini exists and is valid
3. Version constraints match installed Omeka version
4. Cache cleared

**Docker Fix:**
```bash
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/themes/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*
docker compose restart omeka-s
```

**Traditional Fix:**
```bash
sudo chown -R www-data:www-data /var/www/html/omeka-s/themes/
sudo chown -R www-data:www-data /var/www/html/omeka-s/modules/
sudo rm -rf /var/www/html/omeka-s/application/data/cache/*
sudo systemctl restart apache2
```

### Database Connection Error

**Check database.ini:**
- Host (usually "localhost" for traditional, "db" for Docker)
- Username and password
- Database name

**Test connection manually:**

**Docker:**
```bash
docker exec omeka-s-app php -r "
\$ini = parse_ini_file('/var/www/html/config/database.ini');
\$pdo = new PDO('mysql:host='.\$ini['host'].';dbname='.\$ini['dbname'], \$ini['user'], \$ini['password']);
echo 'Connected successfully';
"
```

**Traditional:**
```bash
php -r "
\$ini = parse_ini_file('/var/www/html/omeka-s/config/database.ini');
\$pdo = new PDO('mysql:host='.\$ini['host'].';dbname='.\$ini['dbname'], \$ini['user'], \$ini['password']);
echo 'Connected successfully';
"
```

### File Upload Issues

**Check:**
1. files/ directory exists and is writable
2. PHP upload_max_filesize and post_max_size are sufficient
3. Disk space available

**Docker:**
```bash
docker exec omeka-s-app ls -la /var/www/html/files/
docker exec omeka-s-app chmod -R 775 /var/www/html/files/
docker exec omeka-s-app df -h /var/www/html/
docker exec omeka-s-app php -i | grep upload_max_filesize
```

**Traditional:**
```bash
ls -la /var/www/html/omeka-s/files/
sudo chmod -R 775 /var/www/html/omeka-s/files/
df -h /var/www/html/
php -i | grep upload_max_filesize
```

---

## USEFUL ONE-LINERS

### Find All PHP Files in Theme
**Docker:** `docker exec omeka-s-app find /var/www/html/themes/default -name "*.php"`
**Traditional:** `find /var/www/html/omeka-s/themes/default -name "*.php"`

### Count Items in Database
**Docker:** `docker exec omeka-s-db mariadb -u omekas -pomekas omekas -e "SELECT COUNT(*) FROM resource WHERE resource_type='Omeka\\\\Entity\\\\Item';"`
**Traditional:** `mysql -u user -p omeka_db -e "SELECT COUNT(*) FROM resource WHERE resource_type='Omeka\\\\Entity\\\\Item';"`

### Find Template File Usage
**Docker:** `docker exec omeka-s-app grep -r "partial('common/search" /var/www/html/themes/default/`
**Traditional:** `grep -r "partial('common/search" /var/www/html/omeka-s/themes/default/`

### Check Disk Usage
**Docker:** `docker exec omeka-s-app du -sh /var/www/html/files/*`
**Traditional:** `du -sh /var/www/html/omeka-s/files/*`

---

## DEVELOPMENT WORKFLOW COMPARISON

| Task | Docker | Traditional |
|------|--------|-------------|
| Edit files | Download → Edit → Upload | Direct edit on server or SFTP |
| Permissions | `docker exec` + chown | `sudo chown` |
| Logs | `docker logs` + container logs | Server logs (Apache/Nginx/PHP) |
| Restart | `docker compose restart` | `systemctl restart` |
| Database | Via container | Direct MySQL access |
| Debugging | Container + application logs | Server + application logs |

---

## SKILL USAGE TIP

When using the Omeka S skill with Claude Code:

1. **Identify environment first** - Mention if using Docker or traditional
2. **Provide paths** - Share actual installation path if different from defaults
3. **Check container names** - Docker container names may vary
4. **Mention constraints** - Note any hosting limitations (shared hosting, permissions, etc.)

**Example:**
- "I'm using Docker with containers named `omeka_app` and `omeka_db`"
- "Traditional installation at `/home/user/public_html/omeka-s`"
- "Shared hosting with SSH access but no sudo"

This helps Claude Code provide the most accurate commands for your specific setup.
