# Omeka S Common Workflows & Examples

This document provides step-by-step examples for common Omeka S development tasks.

---

## SITE SETUP WORKFLOWS

### Workflow 0: Understanding Omeka S Site Architecture

**Concept**: In Omeka S, content (items) and presentation (sites) are separate. You can have multiple sites presenting the same items differently.

**Key Components:**

**1. Site Structure**
```
Site
├── Settings (title, slug, theme, visibility)
├── Item Pool (which item sets are available)
├── Pages (content pages with blocks)
├── Navigation (menu structure)
└── Theme (appearance and customization)
```

**2. Item Pool Pattern**
- Sites don't automatically include all items
- Must explicitly add item sets to site's "Item Pool"
- Only items from included item sets appear in site
- Items can belong to multiple sites via item sets
- **In Omeka S 4.x**: Access via site admin → **Resources** tab
- **In earlier versions**: May be labeled "Item Pool" tab

**3. Page & Block Architecture**
- Pages contain multiple content blocks
- Blocks available in Omeka S 4.x:
  - **Asset**: Display uploaded assets (images, files)
  - **Browse Preview**: Dynamic item lists with advanced configuration
    - Resource type filter (items, item sets, media)
    - Item set filter (show only items from specific sets)
    - Search query (basic and advanced)
    - Limit (number of items to display)
    - Components toggle (Heading, Body, Thumbnail)
    - Preview title and link text customization
  - **HTML**: Custom content/text (rich text editor)
  - **Item Showcase**: Manually selected featured items
  - **Item with Metadata**: Single item with full metadata display
  - **Line Break**: Spacing/visual separation
  - **List of Pages**: Auto-generated list of site pages
  - **List of Sites**: Auto-generated list of all public sites
  - **Media Embed**: Embed external media (YouTube, Vimeo, etc.)
  - **Page Date/Time**: Display when page was created/modified
  - **Page Title**: Display the page title
  - **Table of Contents**: Auto-generated from page headings
- Blocks stack vertically on page
- One page can be designated as homepage
- Blocks can be reordered by dragging

**4. Navigation Pattern**
- Site navigation configured separately from pages
- Link types available:
  - **Page**: Links to site pages you created
  - **Browse**: Links to item browse interface
  - **Custom URL**: External or custom internal links
- Can nest links (sub-menus)
- Order matters (drag to rearrange)

**5. Visibility Rules**
- Sites have visibility setting (public/private)
- Pages have individual visibility settings
- Items have visibility settings
- All three must align for content to show publicly:
  - Site must be public
  - Page must be public
  - Item must be public (or item set public)

**Common Patterns:**

**Pattern A: Simple Archive Site**
```
Homepage (welcome page)
├── Page Title block
├── HTML block (introduction/welcome text)
├── Item Showcase block (3-6 featured items)
├── Line Break block
└── Browse Preview block (12-24 recent additions)

About Page
├── Page Title block
├── HTML block (project description, history, credits)
└── List of Pages block (site map)

Navigation:
- Home (page link)
- Browse All (browse link)
- About (page link)
```

**Pattern B: Multi-Collection Site**
```
Homepage
├── Page Title block
├── HTML block (site description)
├── Item Showcase block (featured from Collection A)
├── Line Break block
├── Item Showcase block (featured from Collection B)
└── Browse Preview block (recent from all collections)

Collection A Page
├── Page Title block
├── HTML block (collection-specific description)
├── Asset block (collection banner image)
└── Browse Preview block (filtered to Collection A item set, 24 items)

Collection B Page
├── Page Title block
├── HTML block (collection-specific description)
└── Browse Preview block (filtered to Collection B item set, 24 items)

Navigation:
- Home (page link)
- Collection A (page link)
- Collection B (page link)
- Browse All Items (browse link)
- About (page link)
```

**Pattern C: Exhibit/Narrative Site**
```
Homepage
├── Page Title block
├── HTML block (exhibit introduction)
├── Table of Contents block
└── List of Pages block (exhibit sections)

Exhibit Section Pages (multiple narrative pages)
├── Page Title block
├── HTML block (narrative text with historical context)
├── Item with Metadata block (key primary source with full details)
├── Item Showcase block (supporting materials)
├── Media Embed block (related video/audio if available)
└── HTML block (section conclusion/transition)

Credits Page
├── Page Title block
├── HTML block (acknowledgments, funding, team)
└── Page Date/Time block

Navigation follows narrative/chronological structure:
- Introduction (page)
- Section 1 (page)
- Section 2 (page)
- Section 3 (page)
- Credits (page)
```

**Troubleshooting Common Issues:**

**Problem**: Site shows no items
- **Check**: Item sets added to site's Item Pool (in site admin → **Resources** tab)
- **Check**: Items themselves marked public
- **Check**: Browse Preview block configured correctly
- **Note**: In Omeka S 4.x, the Item Pool is accessed via the **Resources** link in site admin, not a separate "Item Pool" tab

**Problem**: Site shows 404
- **Check**: Site marked as public
- **Check**: Correct URL pattern (`/s/slug`)
- **Fix**: Clear cache, restart if needed

**Problem**: Homepage not showing
- **Check**: Homepage set in site settings
- **Check**: Homepage page marked public
- **Check**: Page has content blocks

**Problem**: Navigation not working
- **Check**: Navigation configured in site settings
- **Check**: Linked pages exist and are public
- **Check**: Browse links use correct format

**Key Database Concepts:**
- Sites stored in `site` table
- Site-to-item-set relationships in `site_item_set`
- Pages in `site_page` table
- Page blocks serialized in `site_page_block`
- Settings in `site_setting` (serialized PHP)

**Working with Sites via Code/CLI:**

Sites are difficult to create programmatically due to serialized settings. Admin interface is strongly recommended for site creation. However, you can:

```bash
# List sites
docker exec omeka-s-db mariadb -u user -p dbname -e "SELECT id, slug, title FROM site;"

# Check site item sets
docker exec omeka-s-db mariadb -u user -p dbname -e "SELECT * FROM site_item_set WHERE site_id=1;"

# Update site visibility
docker exec omeka-s-db mariadb -u user -p dbname -e "UPDATE site SET is_public=1 WHERE id=1;"
```

For complex site setup, admin interface is the proper tool.

### Workflow 0B: Import Content from Omeka Classic

**Task**: Import items from an Omeka Classic site via API

**Prerequisites**:
- Omeka2Importer module installed
- Source Omeka Classic site has API enabled
- API endpoint URL (e.g., `https://example.com/api`)

**Steps:**

1. **Install Omeka2Importer Module** (if not installed)
   ```bash
   # Download module
   git clone https://github.com/omeka-s-modules/Omeka2Importer.git

   # Install to Omeka
   docker cp Omeka2Importer omeka-s-app:/var/www/html/modules/
   docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/Omeka2Importer
   ```

   - Go to Admin → Modules
   - Find Omeka2Importer
   - Click **Install**

2. **Start Import**
   - Go to **Omeka 2 Importer** in left sidebar
   - Click **Import**

3. **Configure Import**
   - **Omeka Classic API endpoint**: `https://example.com/api`
   - **API key**: (leave blank if public API)
   - **Comment**: "Import from [site name]"
   - **Import into**: Select or create item set
   - **Per page**: 50-100 (default is fine)
   - **Import Collections**: ✓ (preserves organization)
   - **Import tag as**: Dublin Core: Subject (recommended)
   - **Import files**: ✓ (if you want media files)

4. **Monitor Import**
   - Click **Import** to start
   - Process runs in background
   - Check **Past Imports** for status
   - Large imports may take hours

5. **Review Import Results**
   - Check logs for errors
   - Common issues:
     - **PDF thumbnail errors**: ImageMagick security policy (see fix below)
     - **Download errors**: URL encoding or missing files
     - **Format errors**: Unsupported file types

   View logs via Docker:
   ```bash
   docker exec omeka-s-app cat /var/www/html/logs/application.log
   ```

6. **Fix PDF Thumbnail Issue** (common after import)
   ```bash
   # Update ImageMagick policy
   docker exec omeka-s-app bash -c 'cat > /etc/ImageMagick-6/policy.xml << EOF
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE policymap [
   <!ELEMENT policymap (policy)+>
   <!ELEMENT policy (#PCDATA)>
   <!ATTLIST policy domain (delegate|coder|filter|path|resource) #IMPLIED>
   <!ATTLIST policy name CDATA #IMPLIED>
   <!ATTLIST policy rights CDATA #IMPLIED>
   <!ATTLIST policy pattern CDATA #IMPLIED>
   <!ATTLIST policy value CDATA #IMPLIED>
   ]>
   <policymap>
     <policy domain="coder" rights="read|write" pattern="PDF" />
     <policy domain="module" rights="read|write" pattern="{PS,PDF,XPS}" />
   </policymap>
   EOF'

   # Restart
   docker compose restart omeka-s
   ```

7. **Post-Import Cleanup**
   - Review imported items
   - Check metadata mappings
   - Verify files downloaded correctly
   - Create site to display content (see Workflow 0)

**Import Statistics Example** (from real CDHA import):
- Items imported: 1,046
- Item sets created: 31
- Duration: ~22 minutes
- Success rate: ~96%
- Common errors: PDF thumbnails (fixable)

---

## THEME CUSTOMIZATION WORKFLOWS

### Workflow 1: Change Theme Colors (Simple CSS)

**Task**: Change the accent color from orange to blue

```bash
# 1. Download current CSS
docker exec omeka-s-app cat /var/www/html/themes/default/asset/css/style.css > style.css

# 2. Find and replace color values
# Edit style.css locally:
# Find: #ff6600 (or existing accent color)
# Replace: #0066ff (your new blue)

# 3. Upload modified CSS
docker cp style.css omeka-s-app:/var/www/html/themes/default/asset/css/style.css

# 4. Clear cache and refresh browser
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*
# Hard refresh browser (Ctrl+Shift+R)
```

**Alternative using theme settings** (if theme supports it):
1. Go to Admin → Sites → Theme
2. Find "Accent Color" setting
3. Change color value
4. Save

### Workflow 2: Customize Item Display Template

**Task**: Add custom metadata display to item show pages

```bash
# 1. Find and copy the default template
docker exec omeka-s-app mkdir -p /var/www/html/themes/default/view/omeka/site/item
docker exec omeka-s-app cp /var/www/html/application/view/omeka/site/item/show.phtml \
    /var/www/html/themes/default/view/omeka/site/item/show.phtml

# 2. Download for editing
docker cp omeka-s-app:/var/www/html/themes/default/view/omeka/site/item/show.phtml .

# 3. Edit show.phtml (add custom HTML/PHP)
```

Example modification to add a custom section:
```php
<?php // After existing content, add: ?>

<div class="custom-metadata">
    <h3>Additional Information</h3>
    <?php $creator = $item->value('dcterms:creator'); ?>
    <?php if ($creator): ?>
        <p class="creator-info">
            <strong>Created by:</strong> <?php echo $creator; ?>
        </p>
    <?php endif; ?>

    <?php // Add custom formatting for dates ?>
    <?php $date = $item->value('dcterms:date'); ?>
    <?php if ($date): ?>
        <p class="date-info">
            <strong>Date:</strong>
            <?php echo date('F j, Y', strtotime($date)); ?>
        </p>
    <?php endif; ?>
</div>
```

```bash
# 4. Upload modified template
docker cp show.phtml omeka-s-app:/var/www/html/themes/default/view/omeka/site/item/show.phtml

# 5. Fix permissions
docker exec omeka-s-app chown www-data:www-data /var/www/html/themes/default/view/omeka/site/item/show.phtml
```

### Workflow 3: Add Custom JavaScript

**Task**: Add a lightbox/gallery feature to images

```bash
# 1. Create or download JS file locally
# Save as custom-gallery.js
```

```javascript
// custom-gallery.js
document.addEventListener('DOMContentLoaded', function() {
    // Simple lightbox functionality
    const images = document.querySelectorAll('.item-media img');

    images.forEach(img => {
        img.addEventListener('click', function() {
            const lightbox = document.createElement('div');
            lightbox.className = 'lightbox';
            lightbox.innerHTML = `
                <div class="lightbox-content">
                    <img src="${this.src}" alt="${this.alt}">
                    <span class="close">&times;</span>
                </div>
            `;
            document.body.appendChild(lightbox);

            lightbox.querySelector('.close').addEventListener('click', function() {
                lightbox.remove();
            });
        });
    });
});
```

```bash
# 2. Copy to theme
docker cp custom-gallery.js omeka-s-app:/var/www/html/themes/default/asset/js/

# 3. Add to layout.phtml
# Download layout
docker cp omeka-s-app:/var/www/html/themes/default/view/layout/layout.phtml .

# Edit layout.phtml, add in <head> section:
```

```php
<?php $this->headScript()->appendFile($this->assetUrl('js/custom-gallery.js')); ?>
```

```bash
# 4. Upload modified layout
docker cp layout.phtml omeka-s-app:/var/www/html/themes/default/view/layout/layout.phtml

# 5. Add CSS for lightbox
# Edit style.css and add:
```

```css
.lightbox {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.9);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.lightbox-content {
    position: relative;
    max-width: 90%;
    max-height: 90%;
}

.lightbox-content img {
    max-width: 100%;
    max-height: 90vh;
}

.lightbox .close {
    position: absolute;
    top: 20px;
    right: 20px;
    color: white;
    font-size: 40px;
    cursor: pointer;
}
```

### Workflow 4: Create a Child Theme

**Task**: Create a customized version of the default theme

```bash
# 1. Create theme structure locally
mkdir -p my-child-theme/{config,asset/{css,js},view/layout}

# 2. Create theme.ini
```

```ini
[info]
name         = "My Custom Theme"
description  = "Child theme based on default theme"
author       = "Your Name"
author_link  = "https://yoursite.com"
version      = "1.0.0"
omeka_version_constraint = "^4.0.0"

[config]
elements.accent_color.name = "accent_color"
elements.accent_color.type = "color"
elements.accent_color.attributes.value = "#0066ff"
```

```bash
# 3. Copy and customize layout from default theme
docker cp omeka-s-app:/var/www/html/themes/default/view/layout/layout.phtml \
    my-child-theme/view/layout/layout.phtml

# Edit as needed...

# 4. Copy base CSS and customize
docker cp omeka-s-app:/var/www/html/themes/default/asset/css/style.css \
    my-child-theme/asset/css/style.css

# Edit CSS with your customizations...

# 5. Upload theme
docker cp my-child-theme omeka-s-app:/var/www/html/themes/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/themes/my-child-theme

# 6. Activate in Admin → Sites → Theme
```

---

## MODULE DEVELOPMENT WORKFLOWS

### Workflow 5: Create a Simple Display Module

**Task**: Create a module that adds a "Share This" button to item pages

```bash
# 1. Create module structure locally
mkdir -p ShareButton/{config,src,view/common,asset/js}
cd ShareButton

# 2. Create config/module.ini
```

```ini
[info]
name         = "Share Button"
description  = "Adds social sharing buttons to item pages"
tags         = "sharing, social"
license      = "GPL-3.0"
author       = "Your Name"
version      = "1.0.0"
omeka_version_constraint = "^4.0.0"
configurable = false
```

```bash
# 3. Create Module.php
```

```php
<?php
namespace ShareButton;

use Omeka\Module\AbstractModule;
use Laminas\EventManager\SharedEventManagerInterface;
use Laminas\EventManager\Event;

class Module extends AbstractModule
{
    public function getConfig()
    {
        return include __DIR__ . '/config/module.config.php';
    }

    public function attachListeners(SharedEventManagerInterface $sharedEventManager)
    {
        // Add share button after item content
        $sharedEventManager->attach(
            'Omeka\Controller\Site\Item',
            'view.show.after',
            [$this, 'addShareButton']
        );
    }

    public function addShareButton(Event $event)
    {
        $view = $event->getTarget();
        echo $view->partial('common/share-button', [
            'item' => $view->item
        ]);
    }
}
```

```bash
# 4. Create config/module.config.php
```

```php
<?php
return [
    'view_manager' => [
        'template_path_stack' => [
            dirname(__DIR__) . '/view',
        ],
    ],
];
```

```bash
# 5. Create view/common/share-button.phtml
```

```php
<?php
$itemUrl = $this->url(null, [], ['force_canonical' => true], true);
$itemTitle = $this->escapeHtml($item->displayTitle());
?>

<div class="share-buttons">
    <h3>Share This Item</h3>
    <a href="https://twitter.com/intent/tweet?url=<?php echo urlencode($itemUrl); ?>&text=<?php echo urlencode($itemTitle); ?>"
       target="_blank"
       class="share-button twitter">
        Share on Twitter
    </a>
    <a href="https://www.facebook.com/sharer/sharer.php?u=<?php echo urlencode($itemUrl); ?>"
       target="_blank"
       class="share-button facebook">
        Share on Facebook
    </a>
    <button onclick="navigator.clipboard.writeText('<?php echo $itemUrl; ?>')"
            class="share-button copy">
        Copy Link
    </button>
</div>

<style>
.share-buttons {
    margin: 20px 0;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 5px;
}

.share-button {
    display: inline-block;
    margin: 5px;
    padding: 10px 20px;
    text-decoration: none;
    color: white;
    border-radius: 3px;
    border: none;
    cursor: pointer;
}

.share-button.twitter { background: #1da1f2; }
.share-button.facebook { background: #4267B2; }
.share-button.copy { background: #666; }
</style>
```

```bash
# 6. Upload module
cd ..
docker cp ShareButton omeka-s-app:/var/www/html/modules/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/ShareButton

# 7. Install in Admin → Modules → ShareButton → Install
```

### Workflow 6: Create a Configurable Module

**Task**: Create a module with admin settings for custom footer text

```bash
# 1. Create module structure
mkdir -p CustomFooter/{config,view/{custom-footer,common}}
cd CustomFooter

# 2. Create config/module.ini
```

```ini
[info]
name         = "Custom Footer"
description  = "Adds custom footer text to all pages"
version      = "1.0.0"
omeka_version_constraint = "^4.0.0"
configurable = true
```

```bash
# 3. Create Module.php with configuration
```

```php
<?php
namespace CustomFooter;

use Omeka\Module\AbstractModule;
use Laminas\View\Model\ViewModel;
use Laminas\Mvc\Controller\AbstractController;
use Laminas\EventManager\SharedEventManagerInterface;
use Laminas\EventManager\Event;

class Module extends AbstractModule
{
    public function getConfig()
    {
        return include __DIR__ . '/config/module.config.php';
    }

    public function getConfigForm(ViewModel $view)
    {
        $services = $this->getServiceLocator();
        $settings = $services->get('Omeka\Settings');

        $view->setVariable('footer_text', $settings->get('custom_footer_text', ''));
        $view->setVariable('footer_style', $settings->get('custom_footer_style', 'default'));

        return $view;
    }

    public function handleConfigForm(AbstractController $controller)
    {
        $services = $this->getServiceLocator();
        $settings = $services->get('Omeka\Settings');

        $params = $controller->params()->fromPost();
        $settings->set('custom_footer_text', $params['footer_text']);
        $settings->set('custom_footer_style', $params['footer_style']);

        return true;
    }

    public function attachListeners(SharedEventManagerInterface $sharedEventManager)
    {
        // Add footer to all site pages
        $sharedEventManager->attach(
            '*',
            'view.layout',
            [$this, 'addFooter']
        );
    }

    public function addFooter(Event $event)
    {
        $view = $event->getTarget();
        $services = $this->getServiceLocator();
        $settings = $services->get('Omeka\Settings');

        $footerText = $settings->get('custom_footer_text', '');
        $footerStyle = $settings->get('custom_footer_style', 'default');

        if ($footerText) {
            echo $view->partial('common/custom-footer', [
                'text' => $footerText,
                'style' => $footerStyle
            ]);
        }
    }
}
```

```bash
# 4. Create config/module.config.php
```

```php
<?php
return [
    'view_manager' => [
        'template_path_stack' => [
            dirname(__DIR__) . '/view',
        ],
    ],
];
```

```bash
# 5. Create view/custom-footer/config-form.phtml (configuration form)
```

```php
<?php
$escape = $this->plugin('escapeHtml');
?>

<div class="field">
    <div class="field-meta">
        <label for="footer_text">Footer Text</label>
    </div>
    <div class="inputs">
        <textarea name="footer_text" id="footer_text" rows="5" cols="60"><?php echo $escape($footer_text); ?></textarea>
        <p class="explanation">Enter the text to display in the custom footer. HTML allowed.</p>
    </div>
</div>

<div class="field">
    <div class="field-meta">
        <label for="footer_style">Footer Style</label>
    </div>
    <div class="inputs">
        <select name="footer_style" id="footer_style">
            <option value="default" <?php echo $footer_style === 'default' ? 'selected' : ''; ?>>Default</option>
            <option value="minimal" <?php echo $footer_style === 'minimal' ? 'selected' : ''; ?>>Minimal</option>
            <option value="prominent" <?php echo $footer_style === 'prominent' ? 'selected' : ''; ?>>Prominent</option>
        </select>
    </div>
</div>
```

```bash
# 6. Create view/common/custom-footer.phtml (display template)
```

```php
<?php
$styleClasses = [
    'default' => 'custom-footer',
    'minimal' => 'custom-footer custom-footer-minimal',
    'prominent' => 'custom-footer custom-footer-prominent'
];
$class = $styleClasses[$style] ?? 'custom-footer';
?>

<div class="<?php echo $class; ?>">
    <div class="footer-content">
        <?php echo $text; ?>
    </div>
</div>

<style>
.custom-footer {
    margin-top: 40px;
    padding: 20px;
    background: #f5f5f5;
    border-top: 1px solid #ddd;
    text-align: center;
}

.custom-footer-minimal {
    padding: 10px;
    font-size: 0.9em;
    color: #666;
}

.custom-footer-prominent {
    padding: 30px;
    background: #333;
    color: white;
    font-size: 1.1em;
}
</style>
```

```bash
# 7. Upload and install
cd ..
docker cp CustomFooter omeka-s-app:/var/www/html/modules/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/CustomFooter

# 8. Install and configure in Admin → Modules → CustomFooter
```

### Workflow 7: Add Custom Field to Item Form

**Task**: Add a "Location Notes" field to the item edit form

```bash
# 1. Create module structure
mkdir -p LocationNotes/{config,src,data/install}
cd LocationNotes

# 2. Create config/module.ini
```

```ini
[info]
name         = "Location Notes"
description  = "Adds a custom location notes field to items"
version      = "1.0.0"
omeka_version_constraint = "^4.0.0"
```

```bash
# 3. Create data/install/schema.sql
```

```sql
CREATE TABLE IF NOT EXISTS location_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    notes TEXT,
    FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE
);
```

```bash
# 4. Create Module.php
```

```php
<?php
namespace LocationNotes;

use Omeka\Module\AbstractModule;
use Laminas\ServiceManager\ServiceLocatorInterface;
use Laminas\EventManager\SharedEventManagerInterface;
use Laminas\EventManager\Event;

class Module extends AbstractModule
{
    public function install(ServiceLocatorInterface $services)
    {
        $connection = $services->get('Omeka\Connection');
        $sql = file_get_contents(__DIR__ . '/data/install/schema.sql');
        $connection->exec($sql);
    }

    public function uninstall(ServiceLocatorInterface $services)
    {
        $connection = $services->get('Omeka\Connection');
        $connection->exec('DROP TABLE IF EXISTS location_notes');
    }

    public function attachListeners(SharedEventManagerInterface $sharedEventManager)
    {
        // Add form field
        $sharedEventManager->attach(
            'Omeka\Controller\Admin\Item',
            'view.add.form.after',
            [$this, 'addFormField']
        );

        $sharedEventManager->attach(
            'Omeka\Controller\Admin\Item',
            'view.edit.form.after',
            [$this, 'addFormField']
        );

        // Save field value
        $sharedEventManager->attach(
            'Omeka\Api\Adapter\ItemAdapter',
            'api.create.post',
            [$this, 'saveLocationNotes']
        );

        $sharedEventManager->attach(
            'Omeka\Api\Adapter\ItemAdapter',
            'api.update.post',
            [$this, 'saveLocationNotes']
        );
    }

    public function addFormField(Event $event)
    {
        $view = $event->getTarget();
        $item = $view->item ?? null;

        // Get existing notes
        $notes = '';
        if ($item) {
            $connection = $this->getServiceLocator()->get('Omeka\Connection');
            $stmt = $connection->prepare('SELECT notes FROM location_notes WHERE item_id = ?');
            $stmt->execute([$item->id()]);
            $result = $stmt->fetch();
            $notes = $result ? $result['notes'] : '';
        }

        echo '<div class="field">';
        echo '<div class="field-meta"><label>Location Notes</label></div>';
        echo '<div class="inputs">';
        echo '<textarea name="location_notes" rows="3" cols="60">' . htmlspecialchars($notes) . '</textarea>';
        echo '<p class="explanation">Additional notes about the location of this item.</p>';
        echo '</div></div>';
    }

    public function saveLocationNotes(Event $event)
    {
        $request = $event->getParam('request');
        $response = $event->getParam('response');
        $item = $response->getContent();

        $notes = $request->getValue('location_notes');
        if ($notes !== null) {
            $connection = $this->getServiceLocator()->get('Omeka\Connection');

            // Delete existing
            $stmt = $connection->prepare('DELETE FROM location_notes WHERE item_id = ?');
            $stmt->execute([$item->id()]);

            // Insert new
            if ($notes) {
                $stmt = $connection->prepare('INSERT INTO location_notes (item_id, notes) VALUES (?, ?)');
                $stmt->execute([$item->id(), $notes]);
            }
        }
    }
}
```

```bash
# 5. Upload and install
cd ..
docker cp LocationNotes omeka-s-app:/var/www/html/modules/
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/LocationNotes
```

---

## TROUBLESHOOTING WORKFLOWS

### Workflow 8: Debug Module Installation Error

**Problem**: Module doesn't appear or shows error when installing

```bash
# Step 1: Check module.ini syntax
docker exec omeka-s-app cat /var/www/html/modules/MyModule/config/module.ini

# Verify required fields exist:
# - name
# - version
# - omeka_version_constraint

# Step 2: Check Module.php syntax
docker exec omeka-s-app php -l /var/www/html/modules/MyModule/Module.php

# Should output: "No syntax errors detected"

# Step 3: Check file permissions
docker exec omeka-s-app ls -la /var/www/html/modules/MyModule

# Should show www-data:www-data ownership
# If not, fix:
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/modules/MyModule

# Step 4: Check application logs
docker exec omeka-s-app cat /var/www/html/logs/application.log | tail -50

# Look for PHP errors or stack traces

# Step 5: Check PHP error logs
docker logs omeka-s-app 2>&1 | tail -50

# Look for fatal errors or warnings

# Step 6: Verify Omeka version compatibility
docker exec omeka-s-app cat /var/www/html/application/Module.php | grep VERSION
# Compare with omeka_version_constraint in module.ini

# Step 7: Check dependencies
docker exec omeka-s-app cat /var/www/html/modules/MyModule/config/module.ini | grep dependencies
# Verify listed modules are installed

# Step 8: Clear cache and restart
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*
docker compose restart omeka-s
```

### Workflow 9: Fix CSS/JS Not Loading

**Problem**: Changes to CSS or JavaScript files don't appear

```bash
# Step 1: Verify file was actually updated
docker exec omeka-s-app cat /var/www/html/themes/default/asset/css/style.css | head -20

# Step 2: Check layout.phtml includes asset correctly
docker exec omeka-s-app grep -A5 headLink /var/www/html/themes/default/view/layout/layout.phtml

# Should show something like:
# <?php $this->headLink()->prependStylesheet($this->assetUrl('css/style.css')); ?>

# Step 3: Check file permissions
docker exec omeka-s-app ls -la /var/www/html/themes/default/asset/css/style.css

# Should be readable by www-data

# Step 4: Clear Omeka cache
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*

# Step 5: Clear browser cache
# Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
# Or open in incognito/private window

# Step 6: Check browser console for 404 errors
# Open browser DevTools (F12)
# Check Network tab for failed asset requests

# Step 7: Verify asset URL is correct
# View page source, find CSS link
# Copy URL and try accessing directly
# Should load the file, not 404

# Step 8: Restart containers if needed
docker compose restart omeka-s
```

### Workflow 10: Recover from Broken Theme

**Problem**: Theme changes broke the site

```bash
# Option 1: Revert to default theme via database
docker exec -i omeka-s-db mariadb -u omekas -pomekas omekas << EOF
UPDATE site_setting SET value = 's:7:"default";' WHERE id = 'theme';
EOF

# Option 2: Replace broken theme files
# Delete broken theme
docker exec omeka-s-app rm -rf /var/www/html/themes/broken-theme

# Copy working theme as backup
docker exec omeka-s-app cp -r /var/www/html/themes/default /var/www/html/themes/default-backup

# Option 3: Restore from backup
# If you have a backup:
docker cp theme-backup omeka-s-app:/var/www/html/themes/my-theme
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/themes/my-theme

# Option 4: Fix permissions if theme disappeared
docker exec omeka-s-app chown -R www-data:www-data /var/www/html/themes/
docker exec omeka-s-app chmod -R 755 /var/www/html/themes/

# Clear cache
docker exec omeka-s-app rm -rf /var/www/html/application/data/cache/*
docker compose restart omeka-s
```

---

## ADVANCED WORKFLOWS

### Workflow 11: Create Custom Search Results Display

**Task**: Customize how search results are displayed

```bash
# 1. Copy search results template
docker exec omeka-s-app mkdir -p /var/www/html/themes/default/view/omeka/site/index
docker exec omeka-s-app cp /var/www/html/application/view/omeka/site/index/search.phtml \
    /var/www/html/themes/default/view/omeka/site/index/search.phtml

# 2. Download for editing
docker cp omeka-s-app:/var/www/html/themes/default/view/omeka/site/index/search.phtml .

# 3. Customize the template
```

Example customization:
```php
<?php
$this->headTitle($this->translate('Search'));
$this->htmlElement('body')->appendAttribute('class', 'search');
?>

<h1><?php echo $this->translate('Search Results'); ?></h1>

<?php echo $this->searchFilters(); ?>

<div class="search-results-grid">
    <?php foreach ($this->results as $result): ?>
        <div class="search-result-card">
            <?php $resource = $result['result']; ?>

            <?php // Display thumbnail if available ?>
            <?php if ($resource->primaryMedia()): ?>
                <div class="result-thumbnail">
                    <?php echo $resource->primaryMedia()->render(); ?>
                </div>
            <?php endif; ?>

            <div class="result-content">
                <h3>
                    <?php echo $resource->link($resource->displayTitle()); ?>
                </h3>

                <?php // Show resource type ?>
                <p class="resource-type">
                    <?php echo get_class($resource); ?>
                </p>

                <?php // Show description excerpt ?>
                <?php if ($description = $resource->value('dcterms:description')): ?>
                    <p class="description">
                        <?php echo $this->escapeHtml($this->truncate($description, 200)); ?>
                    </p>
                <?php endif; ?>

                <?php // Show date if available ?>
                <?php if ($date = $resource->value('dcterms:date')): ?>
                    <p class="date">
                        <strong>Date:</strong> <?php echo $date; ?>
                    </p>
                <?php endif; ?>
            </div>
        </div>
    <?php endforeach; ?>
</div>

<?php echo $this->pagination(); ?>

<style>
.search-results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.search-result-card {
    border: 1px solid #ddd;
    border-radius: 5px;
    overflow: hidden;
    transition: box-shadow 0.3s;
}

.search-result-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.result-thumbnail img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.result-content {
    padding: 15px;
}

.result-content h3 {
    margin-top: 0;
}

.resource-type {
    font-size: 0.85em;
    color: #666;
    text-transform: uppercase;
}

.description {
    color: #444;
    line-height: 1.5;
}
</style>
```

```bash
# 4. Upload modified template
docker cp search.phtml omeka-s-app:/var/www/html/themes/default/view/omeka/site/index/search.phtml
docker exec omeka-s-app chown www-data:www-data /var/www/html/themes/default/view/omeka/site/index/search.phtml
```

---

## PERFORMANCE OPTIMIZATION WORKFLOWS

### Workflow 12: Optimize Image Loading

**Task**: Add lazy loading to images

```bash
# 1. Create a custom JavaScript file
```

```javascript
// lazy-load.js
document.addEventListener('DOMContentLoaded', function() {
    // Add loading="lazy" to all images
    const images = document.querySelectorAll('img:not([loading])');
    images.forEach(img => {
        img.setAttribute('loading', 'lazy');
    });

    // Intersection Observer for custom lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
});
```

```bash
# 2. Add to theme
docker cp lazy-load.js omeka-s-app:/var/www/html/themes/default/asset/js/

# 3. Include in layout.phtml
docker cp omeka-s-app:/var/www/html/themes/default/view/layout/layout.phtml .
# Add: <?php $this->headScript()->appendFile($this->assetUrl('js/lazy-load.js')); ?>
docker cp layout.phtml omeka-s-app:/var/www/html/themes/default/view/layout/layout.phtml
```

---

This workflows document provides practical, tested examples for common Omeka S development tasks. Each workflow includes step-by-step commands and code examples that work with Docker-based installations.
