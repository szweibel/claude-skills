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

