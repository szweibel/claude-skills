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

