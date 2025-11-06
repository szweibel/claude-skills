## TROUBLESHOOTING

### Common Issues & Solutions

**1. Module Not Appearing:**
```bash
# Check module.ini exists and is valid
docker exec omeka-s-app cat /var/www/html/modules/ModuleName/config/module.ini

# Check file permissions
docker exec omeka-s-app ls -la /var/www/html/modules/ModuleName

# Fix permissions
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/ModuleName

# Check Omeka version constraint
# Ensure omeka_version_constraint = "^4.0.0" in module.ini
```

**2. Theme Not Applying:**
```bash
# Check theme.ini exists
docker exec omeka-s-app cat /var/www/html/themes/themename/config/theme.ini

# Check version constraint
# Ensure omeka_version_constraint matches installed version

# Clear cache
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*
docker compose restart omeka-s
```

**3. CSS/JS Changes Not Showing:**
```bash
# Clear browser cache
# Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

# Check file was actually updated
docker exec omeka-s-app cat /var/www/html/themes/default/asset/css/style.css | head -20

# Verify asset URL in layout.phtml
docker exec omeka-s-app grep headLink /var/www/html/themes/default/view/layout/layout.phtml

# Check for caching in local.config.php
docker exec omeka-s-app grep cache /var/www/html/config/local.config.php
```

**4. Database Connection Errors:**
```bash
# Verify database.ini credentials
docker exec omeka-s-app cat /var/www/html/config/database.ini

# Test database connection
docker exec omeka-s-app php -r "
\$pdo = new PDO('mysql:host=db;dbname=omekas', 'omekas', 'omekas');
echo 'Connected successfully';
"

# Check if database container is running
docker ps | grep db

# Check database logs
docker logs omeka-s-db
```

**5. Upload/File Issues:**
```bash
# Check files directory permissions
docker exec omeka-s-app ls -la /var/www/html/volume/files/

# Fix permissions
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/volume/files/

# Check available space
docker exec omeka-s-app df -h /var/www/html/volume/

# Check thumbnail generation
docker exec omeka-s-app which convert  # ImageMagick
```

**6. Module Installation Errors:**
```bash
# Check application logs
docker exec omeka-s-app cat /var/www/html/logs/application.log

# Check PHP errors
docker logs omeka-s-app 2>&1 | tail -50

# Verify Module.php syntax
docker exec omeka-s-app php -l /var/www/html/modules/ModuleName/Module.php

# Check dependencies
docker exec omeka-s-app cat /var/www/html/modules/ModuleName/config/module.ini | grep dependencies
```

**7. View/Template Errors:**
```bash
# Check template path
docker exec omeka-s-app find /var/www/html/themes/default/view -name "*.phtml"

# Verify template syntax (PHP)
docker exec omeka-s-app php -l /var/www/html/themes/default/view/layout/layout.phtml

# Check for missing partials
docker logs omeka-s-app 2>&1 | grep "partial"
```

---

