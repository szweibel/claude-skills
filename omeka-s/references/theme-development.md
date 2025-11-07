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

