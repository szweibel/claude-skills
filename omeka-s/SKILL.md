---
name: omeka-s
description: Expert Omeka S developer assistant for Docker-based installations. Covers theme development (SCSS/CSS, templates), module creation (PHP, events, database), configuration management, and troubleshooting. Use for Omeka S customization from simple CSS tweaks to advanced module development.
---

# Omeka S Development Skill

You are an expert Omeka S developer assistant with comprehensive knowledge of theme development, module creation, configuration, and troubleshooting. This skill enables you to help with Omeka S customization across all complexity levels, from simple CSS tweaks to advanced module development.

## Core Context

### Installation Type
- **Docker-based**: Omeka S runs in containers
- **Container name**: `omeka-s-app` (application), `omeka-s-db` (database)
- **Base path**: `/var/www/html/` inside container
- **Version**: Omeka S 4.0.4+ (check via `docker exec omeka-s-app cat /var/www/html/application/Module.php | grep VERSION`)

### File Operations Pattern
All file operations use Docker commands:
```bash
# Read files
docker exec omeka-s-app cat /var/www/html/{path}

# List directories
docker exec omeka-s-app ls -la /var/www/html/{path}

# Find files
docker exec omeka-s-app find /var/www/html/{path} -name "pattern"

# Copy files into container
docker cp {local-path} omeka-s-app:/var/www/html/{path}

# Fix permissions after copying
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/{path}
```

## Directory Structure

```
/var/www/html/
├── application/           # Core Omeka S code (DON'T MODIFY)
│   ├── asset/            # Admin CSS, JS, fonts
│   ├── config/           # Core configuration
│   ├── src/              # PHP source (namespaced)
│   └── view/             # Default templates (COPY to theme to override)
│       ├── common/       # Shared templates
│       ├── layout/       # Layout templates
│       └── omeka/site/   # Site templates
├── config/               # Installation configuration
│   ├── database.ini      # Database credentials (symlink to volume)
│   └── local.config.php  # Local settings
├── modules/              # Installed modules
├── themes/               # Installed themes
├── volume/               # Persistent data
│   ├── config/           # Persistent config
│   └── files/            # Uploaded media
│       ├── original/
│       ├── large/
│       ├── medium/
│       └── square/
├── vendor/               # Composer dependencies
└── index.php             # Entry point
```

---

## SITE CONFIGURATION & CONTENT VISIBILITY

### Critical Database Relationships

**IMPORTANT: Items, item sets, and sites are connected through multiple database tables. Content won't appear unless ALL relationships are correct.**

#### Making Items Visible on a Site

For items to appear on a public site, ALL of these must be true:

1. **Items must be public**
   ```sql
   UPDATE resource SET is_public = 1 WHERE resource_type = 'Omeka\\Entity\\Item';
   ```

2. **Items must be assigned to the site** (via `item_site` table)
   ```sql
   INSERT INTO item_site (item_id, site_id)
   SELECT i.id, 1 FROM item i
   ON DUPLICATE KEY UPDATE site_id = VALUES(site_id);
   ```

3. **Items must be in open item sets** (if using item sets)
   ```sql
   UPDATE item_set SET is_open = 1;
   ```

4. **Item sets must be linked to site** (via `site_item_set` table)
   ```sql
   INSERT INTO site_item_set (site_id, item_set_id, position)
   SELECT 1, id, id FROM item_set
   ON DUPLICATE KEY UPDATE position = VALUES(position);
   ```

5. **Site's item pool must include item sets** (JSON array in `site` table)
   ```sql
   UPDATE site SET item_pool = '[1,2,3,4,5]' WHERE id = 1;
   -- Or for all item sets:
   SELECT GROUP_CONCAT(id) FROM item_set; -- copy result
   UPDATE site SET item_pool = '[paste,here]' WHERE id = 1;
   ```

#### Key Database Tables

**`site` table:**
- `homepage_id`: Page to show as site homepage (if NULL, shows "no pages" message)
- `item_pool`: JSON array of item set IDs available to this site
- `slug`: URL slug for site
- `is_public`: Site visibility

**`site_setting` table:**
- Key-value settings stored as serialized PHP
- `pagination_per_page`: Items per page (default: 25)
- `browse_heading_property_term`: Property for item titles (e.g., "dcterms:title")
- `browse_body_property_term`: Property for item descriptions
- `browse_defaults_public_items`: JSON with sort_by and sort_order

**`site_page_block` table:**
- `data`: JSON configuration for page blocks
- Common block types: browsePreview, html, itemShowcase, asset
- Browse Preview block options:
  ```json
  {
    "resource_type": "items" or "item_sets",
    "query": "",
    "limit": "12",
    "components": ["resource-heading", "resource-body", "thumbnail"],
    "heading": "Section title",
    "link-text": "View all"
  }
  ```

**`item_site` table (junction):**
- Links items to sites (many-to-many)
- **Critical**: Items won't appear on site without this entry

**`site_item_set` table (junction):**
- Links item sets to sites (many-to-many)
- Has `position` field for ordering

**`item_set` table:**
- `is_open`: Boolean - if FALSE (0), items inside won't show publicly even if site and items are public
- **Critical for visibility**: Must be TRUE (1) to display items

#### Setting Homepage

To set a page as homepage:
```sql
UPDATE site SET homepage_id = (SELECT id FROM site_page WHERE slug = 'welcome' LIMIT 1) WHERE id = 1;
```

Or by page ID directly:
```sql
UPDATE site SET homepage_id = 1 WHERE id = 1;
```

Then clear cache and restart:
```bash
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*
docker restart omeka-s-app
```

---

### Media & Thumbnails System

#### How Thumbnails Work

**Items display thumbnails via `primary_media_id`:**
- Items have `primary_media_id` pointing to a media record
- Media records have `has_thumbnails` boolean flag
- Physical thumbnail files stored in `/files/large/`, `/files/medium/`, `/files/square/`
- Filename format: `{storage_id}.jpg` (matches media.storage_id)

**Item sets don't use primary_media_id:**
- Item sets automatically use first item's thumbnail
- No manual thumbnail assignment needed

**Assets vs Media:**
- `asset` table: Manually uploaded assets (site logos, banners)
- `media` table: Item attachments (images, PDFs, documents)
- Different systems - don't confuse them!

#### Assigning Primary Media to Items

```sql
-- Set first media as primary for all items
UPDATE item i
JOIN (
    SELECT item_id, MIN(id) as first_media
    FROM media
    GROUP BY item_id
) m ON i.id = m.item_id
SET i.primary_media_id = m.first_media;
```

Verify:
```sql
SELECT COUNT(*) FROM item WHERE primary_media_id IS NOT NULL;
```

#### PDF Thumbnail Generation

**Requirements:**
- Ghostscript (`gs`) installed
- ImageMagick with PDF support enabled
- Non-password-protected PDFs

**Install Ghostscript (if missing):**
```bash
docker exec omeka-s-app apt-get update
docker exec omeka-s-app apt-get install -y ghostscript
```

**Update ImageMagick Policy:**

ImageMagick blocks PDF processing by default for security. Update policy:

```bash
docker exec omeka-s-app bash -c 'cat > /etc/ImageMagick-6/policy.xml << "EOF"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policymap [
  <!ELEMENT policymap (policy)*>
  <!ATTLIST policymap xmlns CDATA #FIXED "">
  <!ELEMENT policy EMPTY>
  <!ATTLIST policy xmlns CDATA #FIXED "" domain NMTOKEN #REQUIRED
    name NMTOKEN #IMPLIED pattern CDATA #IMPLIED rights NMTOKEN #IMPLIED
    stealth NMTOKEN #IMPLIED value CDATA #IMPLIED>
]>
<policymap>
  <policy domain="resource" name="memory" value="256MiB"/>
  <policy domain="resource" name="map" value="512MiB"/>
  <policy domain="resource" name="width" value="16KP"/>
  <policy domain="resource" name="height" value="16KP"/>
  <policy domain="resource" name="area" value="128MB"/>
  <policy domain="resource" name="disk" value="1GiB"/>
  <policy domain="coder" rights="read|write" pattern="PDF" />
  <policy domain="module" rights="read|write" pattern="{PS,PDF,XPS}" />
</policymap>
EOF'
```

**Test PDF Processing:**
```bash
docker exec omeka-s-app bash -c '
PDF_FILE=$(ls /var/www/html/files/original/*.pdf 2>/dev/null | head -1)
if [ -n "$PDF_FILE" ]; then
    convert "${PDF_FILE}[0]" -thumbnail 200x200 /tmp/test-thumb.jpg
    if [ -f /tmp/test-thumb.jpg ]; then
        echo "✅ PDF processing works!"
    else
        echo "❌ PDF processing failed"
    fi
fi
'
```

**Generate Thumbnails for All PDFs:**

Create script:
```bash
#!/bin/bash
# Save as /tmp/regenerate-pdf-thumbnails.sh

ORIGINAL_DIR="/var/www/html/files/original"
LARGE_DIR="/var/www/html/files/large"
MEDIUM_DIR="/var/www/html/files/medium"
SQUARE_DIR="/var/www/html/files/square"

success=0
failed=0

for pdf in $ORIGINAL_DIR/*.pdf; do
    if [ -f "$pdf" ]; then
        filename=$(basename "$pdf")
        name="${filename%.*}"

        # Skip password-protected PDFs
        if file "$pdf" | grep -q "password protected"; then
            echo "SKIP: $name (password protected)"
            ((failed++))
            continue
        fi

        # Generate three thumbnail sizes
        if convert "${pdf}[0]" -resize "800x800>" "$LARGE_DIR/${name}.jpg" 2>/dev/null && \
           convert "${pdf}[0]" -resize "200x200>" "$MEDIUM_DIR/${name}.jpg" 2>/dev/null && \
           convert "${pdf}[0]" -resize "200x200^" -gravity center -extent 200x200 "$SQUARE_DIR/${name}.jpg" 2>/dev/null; then
            echo "✓ $name"
            ((success++))
        else
            echo "✗ $name"
            ((failed++))
        fi
    fi
done

echo "Success: $success | Failed: $failed"
```

Upload and run:
```bash
docker cp /tmp/regenerate-pdf-thumbnails.sh omeka-s-app:/tmp/
docker exec omeka-s-app chmod +x /tmp/regenerate-pdf-thumbnails.sh
docker exec omeka-s-app /tmp/regenerate-pdf-thumbnails.sh
```

**Update Database:**
```sql
UPDATE media SET has_thumbnails = 1
WHERE media_type IN ('application/pdf', 'image/jpeg', 'image/png');
```

#### Thumbnail Troubleshooting

**No thumbnails showing:**
1. Check `media.has_thumbnails = 1` for the media
2. Check `item.primary_media_id` points to correct media
3. Verify thumbnail files exist in `/files/medium/` with correct `storage_id.jpg` name
4. Check file permissions (`www-data:www-data`)
5. Clear cache: `docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*`

**Password-protected PDFs:**
- Can't generate thumbnails without password
- Will show placeholder image (audio.png or default.png)
- No automated solution

**Media Type Coverage:**
- ✅ JPEGs, PNGs: Always have thumbnails
- ✅ PDFs: Can generate if not password-protected
- ❌ Audio (MP3, MP4): No visual content - use placeholder
- ❌ Video: Requires ffmpeg - complex setup

#### Common Queries

**Check thumbnail coverage:**
```sql
SELECT
    media_type,
    COUNT(*) as total,
    SUM(has_thumbnails) as with_thumbs,
    COUNT(*) - SUM(has_thumbnails) as without_thumbs
FROM media
GROUP BY media_type
ORDER BY (COUNT(*) - SUM(has_thumbnails)) DESC;
```

**Find items without primary media:**
```sql
SELECT COUNT(*) FROM item WHERE primary_media_id IS NULL;
```

**Find items without thumbnails:**
```sql
SELECT i.id, i.primary_media_id, m.has_thumbnails
FROM item i
LEFT JOIN media m ON i.primary_media_id = m.id
WHERE m.has_thumbnails = 0 OR i.primary_media_id IS NULL;
```

---

## THEME DEVELOPMENT

### Theme Structure (Official Pattern)

```
themes/{theme-name}/
├── config/
│   └── theme.ini         # REQUIRED - Theme metadata & settings
├── asset/
│   ├── css/              # Compiled CSS
│   │   ├── style.css
│   │   └── print.css
│   ├── sass/             # SASS source (optional but recommended)
│   │   ├── style.scss    # Main entry point
│   │   ├── print.scss
│   │   ├── _base.scss
│   │   ├── _screen.scss
│   │   └── _desktop.scss
│   ├── js/
│   │   └── {theme}.js
│   ├── img/
│   └── fonts/
├── view/
│   ├── layout/
│   │   └── layout.phtml  # Main layout template
│   ├── common/           # Shared partials
│   └── omeka/site/       # Override core templates
│       ├── item/
│       │   ├── show.phtml
│       │   └── browse.phtml
│       └── ...
├── composer.json         # PHP dependencies (optional)
├── package.json          # Node dependencies for SASS compilation
├── gulpfile.js           # Build system (if using SASS)
└── theme.jpg             # Theme thumbnail
```

### CSS/SCSS Build Process

**IMPORTANT: Official Omeka S themes use SCSS source files with Gulp for CSS compilation. Never edit CSS files directly - edit SCSS sources and rebuild.**

#### Build System Structure

Default theme uses:
- **SCSS source**: `asset/sass/` directory
- **Build tool**: Gulp (`gulpfile.js`)
- **Output**: `asset/css/` directory (compiled, autoprefixed, compressed)
- **Dependencies**: `package.json` defines npm packages

#### SCSS Architecture (Default Theme Pattern)

```
asset/sass/
├── style.scss           # Main entry - imports all partials
├── print.scss           # Print styles entry
├── _normalize.scss      # CSS reset
├── _base.scss           # Variables, typography, colors
├── _screen.scss         # Mobile-first styles
└── _desktop.scss        # Desktop overrides (min-width: 800px)
```

**Import order in style.scss:**
```scss
@import "normalize";     // Reset
@import "susy";          // Grid system
@import "base";          // Variables & base styles

@media screen {
    @import "screen";    // Mobile-first styles
}

@media screen and (min-width:800px) {
    @import "desktop";   // Desktop enhancements
}
```

#### Workflow for CSS Changes

**1. Download theme files from container:**
```bash
docker cp omeka-s-app:/var/www/html/themes/default /tmp/omeka-theme
cd /tmp/omeka-theme
```

**2. Install build dependencies:**
```bash
npm install
# If sass module missing:
npm install sass
```

**3. Edit SCSS source files:**
```bash
# Edit the appropriate partial:
nano asset/sass/_screen.scss    # For mobile/base styles
nano asset/sass/_desktop.scss   # For desktop styles
nano asset/sass/_base.scss      # For variables/colors
```

**4. Compile SCSS to CSS:**
```bash
npx gulp css
# Or watch for changes:
npx gulp css:watch
```

**5. Upload compiled CSS back to container:**
```bash
docker cp asset/css/style.css omeka-s-app:/var/www/html/themes/default/asset/css/
docker exec omeka-s-app chown www-data:www-data /var/www/html/themes/default/asset/css/style.css
```

**6. Clear Omeka cache:**
```bash
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*
```

#### Common SCSS Variables (in _base.scss)

```scss
// Spacing
$spacing-s: 7.5px;
$spacing-m: 15px;
$spacing-l: 30px;

// Colors
$gray: #ababab;
$bold: darken($gray, 20%);  // #676767
$light: lighten($gray, 20%); // #dedede
$bg: lighten($gray, 30%);    // #f8f8f8
$link: #920b0b;              // Accent color

// Typography
$base-font-size: 20px;
$base-line-height: 30px;
```

#### Example: Convert List to Grid Layout

**Edit `asset/sass/_screen.scss` (mobile-first):**
```scss
ul.resource-list {
    list-style-type: none;
    padding-left: 0;
    display: grid;
    grid-template-columns: 1fr;  // 1 column mobile
    gap: $spacing-l;
}

ul.resource-list .resource {
    border: 1px solid $light;
    padding: 0;
    background: #fff;
    display: flex;
    flex-direction: column;

    &:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
}

ul.resource-list .resource img {
    width: 100%;
    height: auto;
    max-height: 250px;
    object-fit: cover;
}

// 2 columns for tablets
@media screen and (min-width: 600px) {
    ul.resource-list {
        grid-template-columns: repeat(2, 1fr);
    }
}
```

**Edit `asset/sass/_desktop.scss` (desktop enhancements):**
```scss
ul.resource-list {
    grid-template-columns: repeat(3, 1fr);  // 3 columns at 800px+
}

// 4 columns for large screens
@media screen and (min-width: 1200px) {
    ul.resource-list {
        grid-template-columns: repeat(4, 1fr);
    }
}
```

#### Gulpfile.js Configuration

Default theme uses this Gulp setup:
```javascript
var gulp = require('gulp');

gulp.task('css', function () {
    var sass = require('gulp-sass')(require('sass'));
    var postcss = require('gulp-postcss');
    var autoprefixer = require('autoprefixer');

    return gulp.src('./asset/sass/*.scss')
        .pipe(sass({
            outputStyle: 'compressed',
            includePaths: ['node_modules/susy/sass']
        }).on('error', sass.logError))
        .pipe(postcss([
            autoprefixer()
        ]))
        .pipe(gulp.dest('./asset/css'));
});

gulp.task('css:watch', function () {
    gulp.watch('./asset/sass/*.scss', gulp.parallel('css'));
});
```

**Features:**
- **Compressed output**: Minified CSS
- **Autoprefixer**: Adds vendor prefixes automatically
- **Susy grid**: Legacy grid system (optional)
- **Watch mode**: Auto-recompile on changes

#### Quick CSS Editing (Without Build System)

For minor tweaks, you can:
1. Edit compiled CSS directly in container (not recommended for major changes)
2. Use theme.ini config options for colors, spacing
3. Add custom CSS via site admin → Appearance → [Theme] → Custom CSS

**Direct edit example:**
```bash
# Download, edit, upload
docker cp omeka-s-app:/var/www/html/themes/default/asset/css/style.css ./
# Edit style.css
docker cp style.css omeka-s-app:/var/www/html/themes/default/asset/css/
docker exec omeka-s-app chown www-data:www-data /var/www/html/themes/default/asset/css/style.css
```

**Note:** Direct CSS edits will be lost if SCSS is recompiled.

#### Troubleshooting Build Issues

**"npm: command not found" in container:**
- Compile on host machine, upload CSS only
- Container doesn't need Node.js for production

**SCSS compilation errors:**
- Check syntax in edited files
- Ensure all variables are defined
- Verify @import paths are correct

**Changes not appearing:**
- Clear browser cache (Ctrl+Shift+R)
- Clear Omeka cache: `docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*`
- Restart container: `docker restart omeka-s-app`
- Check file permissions: `docker exec omeka-s-app ls -la /var/www/html/themes/default/asset/css/`

**Deprecation warnings during build:**
- SASS/Gulp warnings are normal for older themes
- Output CSS still works correctly
- Can be ignored unless build fails

### theme.ini (Required Configuration)

```ini
[info]
name         = "Theme Name"
description  = "Theme description"
author       = "Author Name"
author_link  = "https://example.com"
theme_link   = "https://github.com/..."
version      = "1.0.0"
omeka_version_constraint = "^4.0.0"
tags         = "tag1, tag2"

[config]
elements.accent_color.name = "accent_color"
elements.accent_color.type = "color"
elements.accent_color.attributes.value = "#ff6600"

elements.logo.name = "logo"
elements.logo.type = "asset"
elements.logo.attributes.accept = "image/*"
```

### layout.phtml (Main Layout Template)

Key patterns in layout.phtml:
```php
<!DOCTYPE html>
<html lang="<?php echo $this->lang(); ?>">
<head>
    <meta charset="utf-8">
    <title><?php echo $this->pageTitle($site->title(), 2); ?></title>

    <?php // Load CSS ?>
    <?php $this->headLink()->prependStylesheet($this->assetUrl('css/style.css')); ?>
    <?php $this->headLink()->prependStylesheet('//fonts.googleapis.com/css?family=Lato'); ?>
    <?php echo $this->headLink(); ?>

    <?php // Load JavaScript ?>
    <?php $this->headScript()->prependFile($this->assetUrl('js/default.js')); ?>
    <?php echo $this->headScript(); ?>

    <?php // Theme settings ?>
    <?php $accentColor = $this->themeSetting('accent_color'); ?>
</head>
<body>
    <header>
        <?php // Logo ?>
        <?php if ($logo = $this->themeSetting('logo')): ?>
            <img src="<?php echo $this->themeSettingAssetUrl('logo'); ?>" alt="Logo">
        <?php endif; ?>

        <?php // Site title ?>
        <h1><?php echo $site->title(); ?></h1>

        <?php // Navigation ?>
        <?php echo $this->navigation()->menu()->renderMenu(null, [
            'maxDepth' => $this->themeSetting('nav_depth')
        ]); ?>

        <?php // Search ?>
        <?php echo $this->partial('common/search-form'); ?>
    </header>

    <main>
        <?php // Page content ?>
        <?php echo $this->content; ?>
    </main>

    <footer>
        <?php echo $this->themeSetting('footer_content'); ?>
    </footer>
</body>
</html>
```

### Common View Helpers (Use via $this->)

- `$this->assetUrl('path/file.ext')` - Theme asset URLs
- `$this->themeSetting('setting_name')` - Get theme setting value
- `$this->themeSettingAssetUrl('logo')` - URL for theme setting assets
- `$this->url('route', ['param' => 'value'])` - Generate URLs
- `$this->translate('text')` - Translate strings
- `$this->escapeHtml($text)` - HTML escaping
- `$this->partial('common/template-name')` - Render partial
- `$this->pageTitle($text, $level)` - Set page title
- `$this->thumbnail($resource, ['thumbnailType' => 'square'])` - Display thumbnails
- `$this->lang()` - Current language code
- `$this->navigation()->menu()` - Navigation helper
- `$this->headLink()` - CSS link helper
- `$this->headScript()` - JavaScript helper

### Customizing Themes Workflow

**1. Simple CSS Changes (No SASS):**
```bash
# Read current CSS
docker exec omeka-s-app cat /var/www/html/themes/default/asset/css/style.css > style.css

# Edit style.css locally
# ... make changes ...

# Copy back
docker cp style.css omeka-s-app:/var/www/html/themes/default/asset/css/style.css

# Clear cache if needed
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*
```

**2. SASS Changes (Recommended):**
```bash
# Extract SASS files
docker exec omeka-s-app tar -czf /tmp/sass.tar.gz -C /var/www/html/themes/default/asset sass
docker cp omeka-s-app:/tmp/sass.tar.gz .
tar -xzf sass.tar.gz

# Edit SASS files locally
# ... make changes to *.scss files ...

# Compile (if you have Node/gulp locally)
npm install
gulp

# OR copy SASS back and compile in container (if tools installed)
docker cp sass omeka-s-app:/var/www/html/themes/default/asset/
docker exec -w /var/www/html/themes/default omeka-s-app npm install
docker exec -w /var/www/html/themes/default omeka-s-app gulp
```

**3. Template Changes:**
```bash
# Find template to customize
docker exec omeka-s-app find /var/www/html/application/view/omeka/site -name "*.phtml"

# Copy template to theme
docker exec omeka-s-app mkdir -p /var/www/html/themes/default/view/omeka/site/item
docker exec omeka-s-app cp /var/www/html/application/view/omeka/site/item/show.phtml \
    /var/www/html/themes/default/view/omeka/site/item/show.phtml

# Download, edit, and upload
docker cp omeka-s-app:/var/www/html/themes/default/view/omeka/site/item/show.phtml .
# ... edit show.phtml ...
docker cp show.phtml omeka-s-app:/var/www/html/themes/default/view/omeka/site/item/show.phtml
```

**4. Creating New Theme:**
```bash
# Create theme structure locally
mkdir -p my-theme/{config,asset/{css,js,img},view/layout}

# Create theme.ini (see pattern above)
# Create layout.phtml (see pattern above)
# Create style.css

# Copy to container
docker cp my-theme omeka-s-app:/var/www/html/themes/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/themes/my-theme

# Theme now appears in Omeka admin
```

---

## MODULE DEVELOPMENT

### Module Structure (Official Pattern)

```
modules/{ModuleName}/
├── Module.php            # REQUIRED - Main module class
├── config/
│   ├── module.ini        # REQUIRED - Module metadata
│   └── module.config.php # Module configuration (recommended)
├── src/                  # Namespaced PHP code
│   ├── Controller/       # Controllers
│   │   └── IndexController.php
│   ├── Form/             # Forms
│   │   └── ConfigForm.php
│   ├── Entity/           # Doctrine entities
│   ├── Service/          # Service factories
│   ├── View/
│   │   └── Helper/       # View helpers
│   └── Job/              # Background jobs
├── view/
│   ├── {module-name}/    # Module templates
│   │   └── index/
│   │       └── index.phtml
│   └── common/           # Shared templates (prefix with module name!)
├── asset/
│   ├── js/
│   │   └── {module-name}.js
│   └── css/
│       └── {module-name}.css
├── data/
│   ├── install/
│   │   └── schema.sql    # Database schema
│   └── scripts/
│       └── upgrade.php   # Upgrade logic
├── language/             # Translations
│   ├── template.pot
│   └── en_US.mo
├── test/                 # Unit tests
├── vendor/               # Composer dependencies (git-ignored)
├── composer.json
├── LICENSE.txt
└── README.md
```

### module.ini (Required)

```ini
[info]
name         = "Module Name"
description  = "Module description"
tags         = "tag1, tag2"
license      = "Apache-2.0"
author       = "Author Name"
author_link  = "https://example.com"
module_link  = "https://github.com/..."
support_link = "https://github.com/.../issues"
configurable = true
version      = "1.0.0"
omeka_version_constraint = "^4.0.0"
dependencies = "OtherModule"
```

### Module.php (Required Class)

```php
<?php
namespace ModuleName;

use Omeka\Module\AbstractModule;
use Laminas\View\Model\ViewModel;
use Laminas\ServiceManager\ServiceLocatorInterface;
use Laminas\EventManager\SharedEventManagerInterface;
use Laminas\EventManager\Event;

class Module extends AbstractModule
{
    /**
     * Return module configuration array
     */
    public function getConfig()
    {
        return include __DIR__ . '/config/module.config.php';
    }

    /**
     * Install module (create tables, set defaults)
     */
    public function install(ServiceLocatorInterface $services)
    {
        $connection = $services->get('Omeka\Connection');
        $sql = file_get_contents(__DIR__ . '/data/install/schema.sql');
        $connection->exec($sql);

        // Set default settings
        $settings = $services->get('Omeka\Settings');
        $settings->set('modulename_setting', 'default_value');
    }

    /**
     * Uninstall module (remove tables, settings)
     */
    public function uninstall(ServiceLocatorInterface $services)
    {
        $settings = $services->get('Omeka\Settings');
        $settings->delete('modulename_setting');

        $connection = $services->get('Omeka\Connection');
        $connection->exec('DROP TABLE IF EXISTS modulename_table');
    }

    /**
     * Upgrade module
     */
    public function upgrade($oldVersion, $newVersion, ServiceLocatorInterface $services)
    {
        require_once __DIR__ . '/data/scripts/upgrade.php';
    }

    /**
     * Return configuration form view (if configurable=true)
     */
    public function getConfigForm(ViewModel $view)
    {
        $services = $this->getServiceLocator();
        $settings = $services->get('Omeka\Settings');

        $view->setVariable('setting_value', $settings->get('modulename_setting'));

        return $view;
    }

    /**
     * Handle configuration form submission
     */
    public function handleConfigForm(AbstractController $controller)
    {
        $services = $this->getServiceLocator();
        $settings = $services->get('Omeka\Settings');

        $params = $controller->params()->fromPost();
        $settings->set('modulename_setting', $params['modulename_setting']);

        return true;
    }

    /**
     * Attach event listeners
     */
    public function attachListeners(SharedEventManagerInterface $sharedEventManager)
    {
        // Listen to item view event
        $sharedEventManager->attach(
            'Omeka\Controller\Site\Item',
            'view.show.after',
            [$this, 'handleItemShowAfter']
        );

        // Listen to form events
        $sharedEventManager->attach(
            'Omeka\Form\ItemForm',
            'form.add_elements',
            [$this, 'addFormElements']
        );
    }

    /**
     * Event handler example
     */
    public function handleItemShowAfter(Event $event)
    {
        $view = $event->getTarget();
        $item = $view->item;

        // Add custom content
        echo $view->partial('common/modulename-display', ['item' => $item]);
    }

    public function addFormElements(Event $event)
    {
        $form = $event->getTarget();
        $form->add([
            'name' => 'modulename_field',
            'type' => 'Text',
            'options' => [
                'label' => 'Custom Field',
            ],
        ]);
    }
}
```

### module.config.php (Recommended Configuration)

```php
<?php
return [
    'view_manager' => [
        'template_path_stack' => [
            dirname(__DIR__) . '/view',
        ],
    ],
    'controllers' => [
        'invokables' => [
            'ModuleName\Controller\Index' => Controller\IndexController::class,
        ],
    ],
    'router' => [
        'routes' => [
            'modulename' => [
                'type' => 'Segment',
                'options' => [
                    'route' => '/modulename[/:action]',
                    'defaults' => [
                        'controller' => 'ModuleName\Controller\Index',
                        'action' => 'index',
                    ],
                ],
            ],
        ],
    ],
    'view_helpers' => [
        'invokables' => [
            'moduleNameHelper' => View\Helper\ModuleNameHelper::class,
        ],
    ],
    'form_elements' => [
        'invokables' => [
            'ModuleName\Form\ConfigForm' => Form\ConfigForm::class,
        ],
    ],
];
```

### Common Omeka S Events (For attachListeners)

**Controller Events:**
- `view.show.before` / `view.show.after` - Before/after showing resource
- `view.browse.before` / `view.browse.after` - Before/after browse page
- `view.search.query` - Modify search query
- `view.layout` - Add content to layout

**Form Events:**
- `form.add_elements` - Add form elements
- `form.add_input_filters` - Add input filters

**API Events:**
- `api.search.query` - Modify API search
- `api.find.query` - Modify API find
- `api.create.pre` / `api.create.post` - Before/after creation
- `api.update.pre` / `api.update.post` - Before/after update
- `api.delete.pre` / `api.delete.post` - Before/after deletion

**Resource Events:**
- `rep.resource.display_values` - Modify resource display
- `rep.resource.values` - Modify resource values

### Module Development Workflow

**1. Create Module Structure:**
```bash
# Create module directory locally
mkdir -p MyModule/{config,src,view,asset/{js,css},data/install}

# Create Module.php (see template above)
# Create config/module.ini (see template above)
# Create config/module.config.php (optional but recommended)

# Copy to container
docker cp MyModule omeka-s-app:/var/www/html/modules/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/MyModule

# Module now appears in Omeka admin > Modules
```

**2. Modify Existing Module:**
```bash
# Download module
docker cp omeka-s-app:/var/www/html/modules/ModuleName ./ModuleName

# Edit files
# ... make changes ...

# Upload changes
docker cp ModuleName omeka-s-app:/var/www/html/modules/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/ModuleName

# Deactivate and reactivate module in admin to reload
```

**3. Debug Module:**
```bash
# Check logs
docker exec omeka-s-app cat /var/www/html/logs/application.log

# Enable error logging in config/local.config.php
docker exec omeka-s-app cat /var/www/html/config/local.config.php
# Add: 'logger' => ['log' => true, 'priority' => \Laminas\Log\Logger::DEBUG]
```

---

## CONFIGURATION MANAGEMENT

### database.ini
Location: `/var/www/html/config/database.ini` → symlink to `/var/www/html/volume/config/database.ini`

```ini
user     = "omekas"
password = "omekas"
dbname   = "omekas"
host     = "db"
;port     =
;unix_socket =
;log_path =
```

To modify:
```bash
docker exec omeka-s-app bash -c 'cat > /var/www/html/config/database.ini << EOF
user     = "newuser"
password = "newpass"
dbname   = "newdb"
host     = "db"
EOF'
```

### local.config.php
Location: `/var/www/html/config/local.config.php`

Common configurations:
```php
<?php
return [
    'logger' => [
        'log' => true,  // Enable logging
        'priority' => \Laminas\Log\Logger::DEBUG,  // Log level
    ],
    'thumbnails' => [
        'types' => [
            'large' => ['constraint' => 800],
            'medium' => ['constraint' => 200],
            'square' => ['constraint' => 200, 'options' => ['gravity' => 'center']],
        ],
        'thumbnailer_options' => [
            'imagemagick_dir' => '/usr/bin',
        ],
    ],
    'translator' => [
        'locale' => 'en_US',
    ],
    'mail' => [
        'transport' => [
            'type' => 'smtp',
            'options' => [
                'name' => 'localhost',
                'host' => 'smtp.example.com',
                'port' => 587,
            ],
        ],
    ],
    'service_manager' => [
        'aliases' => [
            'Omeka\File\Store' => 'Omeka\File\Store\Local',
            'Omeka\File\Thumbnailer' => 'Omeka\File\Thumbnailer\ImageMagick',
        ],
    ],
];
```

---

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

## BEST PRACTICES

### Naming Conventions
- **Modules**: CamelCase (MyAwesomeModule)
- **Themes**: lowercase-with-hyphens (my-theme)
- **Files**: lowercase, underscores for PHP classes, hyphens for templates
- **Namespaces**: Follow PSR-4 (ModuleName\Controller\IndexController)

### File Organization
- Keep themes self-contained in themes directory
- Keep modules self-contained in modules directory
- Never modify core application files
- Use version control for custom code

### Performance
- Minimize database queries in loops
- Use Omeka's built-in caching
- Optimize images before upload
- Use appropriate thumbnail sizes
- Lazy load heavy resources

### Security
- Always escape output: `$this->escapeHtml()`
- Validate user input
- Use prepared statements for database queries
- Check permissions before sensitive operations
- Follow Laminas security practices

### Maintainability
- Document custom code
- Follow Omeka's coding standards
- Keep modules focused (single responsibility)
- Test across Omeka versions
- Provide upgrade paths

---

## QUICK REFERENCE

### Essential Commands

```bash
# Check Omeka version
docker exec omeka-s-app cat /var/www/html/application/Module.php | grep VERSION

# List installed modules
docker exec omeka-s-app ls /var/www/html/modules/

# List installed themes
docker exec omeka-s-app ls /var/www/html/themes/

# Check logs
docker logs omeka-s-app --tail=50
docker exec omeka-s-app cat /var/www/html/logs/application.log

# Clear cache
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*

# Restart Omeka
docker compose restart omeka-s

# Database backup
docker exec omeka-s-db mariadb-dump -u omekas -pomekas omekas > backup.sql

# Database restore
docker exec -i omeka-s-db mariadb -u omekas -pomekas omekas < backup.sql
```

### File Paths Reference

- Themes: `/var/www/html/themes/`
- Modules: `/var/www/html/modules/`
- Config: `/var/www/html/config/`
- Uploads: `/var/www/html/volume/files/`
- Logs: `/var/www/html/logs/`
- Application: `/var/www/html/application/`
- Default templates: `/var/www/html/application/view/omeka/site/`

---

## GETTING STARTED

When helping with Omeka S development:

1. **Understand the task**: Clarify if it's theme, module, config, or troubleshooting
2. **Check current state**: Read relevant files before modifying
3. **Use Docker commands**: All operations go through `docker exec` or `docker cp`
4. **Follow patterns**: Use official Omeka structures and conventions
5. **Test changes**: Verify changes work as expected
6. **Document**: Explain what was changed and why

Remember: Omeka S uses Laminas Framework (formerly Zend). Many patterns follow Laminas MVC conventions.

---

## ADDITIONAL RESOURCES

- Official Docs: https://omeka.org/s/docs/
- Developer Docs: https://omeka.org/s/docs/developer/
- GitHub: https://github.com/omeka/omeka-s
- Forum: https://forum.omeka.org/
- Module Repository: https://omeka.org/s/modules/
- Theme Repository: https://omeka.org/s/themes/
