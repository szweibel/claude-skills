# Omeka S Development Skill for Claude Code

A comprehensive Claude Code skill for developing, customizing, and troubleshooting Omeka S installations. Supports both Docker-based and traditional server installations across all complexity levels.

## What This Skill Provides

This skill enables Claude Code to assist with:

### Theme Development
- CSS/SASS customization
- Template modification
- Layout changes
- Asset management
- Creating new themes
- Responsive design

### Module Development
- Creating custom modules
- Modifying existing modules
- Event system integration
- API development
- Form creation
- Database operations

### Configuration
- Database setup
- Local configuration
- Performance tuning
- Security settings
- File storage configuration

### Troubleshooting
- Debugging errors
- Fixing permissions
- Database issues
- Module/theme problems
- Performance optimization

## Installation

The skill is already set up in this directory structure:

```
.claude/skills/omeka-s/
├── skill.md                    # Main skill prompt (comprehensive knowledge base)
├── examples/
│   └── workflows.md            # Step-by-step workflow examples
├── reference/
│   └── quick-reference.md      # Quick command reference
└── README.md                   # This file
```

## How to Use This Skill

### Method 1: Automatic (Claude Code will detect it)

Claude Code automatically loads skills from the `.claude/skills/` directory. Simply start a conversation about Omeka S development:

```
You: "I need to change the accent color in my Omeka theme"
Claude: [Uses the Omeka S skill to provide specific guidance]
```

### Method 2: Explicit Invocation

You can explicitly invoke the skill:

```bash
/skill omeka-s
```

Then ask your Omeka S question.

### Method 3: Reference in Prompt

Reference the skill explicitly in your request:

```
You: "Using the Omeka S skill, help me create a module that adds custom metadata fields"
```

## Supported Installation Types

This skill works with:

### Docker-Based Installations
- Standard Docker Compose setups
- Custom container configurations
- Development environments
- Production containerized deployments

**Tell Claude Code:** "I'm using Docker with containers named `omeka-s-app` and `omeka-s-db`"

### Traditional Server Installations
- Apache/Nginx + PHP + MySQL
- Shared hosting
- VPS/dedicated servers
- Local development (XAMPP, MAMP, etc.)

**Tell Claude Code:** "I have a traditional installation at `/var/www/html/omeka-s`"

## Usage Examples

### Example 1: Simple CSS Change

**You:** "Change the default theme's main color from red to blue"

**Claude Code will:**
1. Check current theme configuration
2. Provide commands to download/modify CSS
3. Upload changes back
4. Clear cache
5. Verify changes

### Example 2: Create Custom Module

**You:** "Create a module that adds a 'Featured' checkbox to items"

**Claude Code will:**
1. Generate complete module structure
2. Provide all necessary code files
3. Include database schema
4. Give installation instructions
5. Explain how to test

### Example 3: Debug Issue

**You:** "My module isn't showing up in the admin interface"

**Claude Code will:**
1. Check module.ini configuration
2. Verify file permissions
3. Check PHP syntax
4. Review application logs
5. Provide fix commands

### Example 4: Customize Item Display

**You:** "I want to add a custom metadata section to item pages"

**Claude Code will:**
1. Identify template to modify
2. Provide template code
3. Show how to add custom styling
4. Include view helper examples
5. Explain testing process

## Key Features

### Context-Aware
The skill understands:
- Docker vs. traditional installations
- Omeka S version differences
- Module dependencies
- Theme inheritance
- File structure variations

### Progressive Complexity
Supports tasks from:
- **Simple**: CSS color changes, text updates
- **Moderate**: Template modifications, basic modules
- **Advanced**: Custom APIs, complex modules, database operations
- **Expert**: Performance optimization, security hardening

### Best Practices Built-In
Claude Code will:
- Follow Omeka coding standards
- Use proper naming conventions
- Suggest security best practices
- Recommend performance optimizations
- Provide maintainable code

## Documentation Structure

### skill.md (Main Knowledge Base)
Complete reference covering:
- Installation detection
- Directory structure
- Theme architecture
- Module development
- Configuration management
- Troubleshooting guide
- View helpers
- Events system
- Best practices

### examples/workflows.md
Step-by-step workflows:
- Theme customization workflows
- Module development workflows
- Troubleshooting workflows
- Advanced development patterns
- Performance optimization

### reference/quick-reference.md
Quick command reference:
- Docker vs. traditional commands
- File locations
- Common operations
- One-liners
- SQL queries
- Service management

## Tips for Best Results

### 1. Specify Your Environment

**Good:**
- "I'm using Docker with default container names"
- "Traditional install at `/opt/omeka-s` on Ubuntu 22.04"
- "Shared hosting with no sudo access"

**Less Helpful:**
- "I'm using Omeka"

### 2. Be Specific About Goals

**Good:**
- "Add a 'Share This' button to item pages with Twitter and Facebook links"
- "Change the header background to #003366 and make logo 200px wide"

**Less Helpful:**
- "Make the site look better"
- "Fix my theme"

### 3. Provide Error Context

**Good:**
- "Module install fails with error: 'omeka_version_constraint not met'"
- "Getting 500 error, logs show: [stack trace]"

**Less Helpful:**
- "It doesn't work"
- "I'm getting an error"

### 4. Mention Constraints

**Good:**
- "I can't restart Apache (shared hosting)"
- "Need to maintain PHP 7.4 compatibility"
- "Must preserve existing customizations in theme"

This helps Claude Code provide solutions that work within your limitations.

## Workflow Pattern

For complex tasks, Claude Code typically follows this pattern:

1. **Understand**: Clarify requirements and environment
2. **Analyze**: Check current state of files/configuration
3. **Plan**: Outline steps to achieve goal
4. **Implement**: Provide commands and code
5. **Test**: Suggest verification steps
6. **Document**: Explain what was changed and why

## Common Use Cases

### Theme Development
- Customizing colors, fonts, layouts
- Adding custom CSS/JavaScript
- Modifying templates
- Creating child themes
- Responsive design fixes

### Module Development
- Custom metadata fields
- Display modifications
- Data import/export
- API integrations
- Workflow automation

### Site Administration
- Backup/restore procedures
- User management
- Performance tuning
- Security hardening
- Migration assistance

### Debugging
- Error diagnosis
- Log analysis
- Permission fixes
- Database issues
- Module conflicts

## Limitations

This skill covers:
- ✅ Omeka S (version 1.x through 4.x)
- ✅ Standard modules and themes
- ✅ Docker and traditional installations
- ✅ PHP, JavaScript, CSS/SASS
- ✅ MySQL/MariaDB operations

This skill does NOT cover:
- ❌ Omeka Classic (different architecture)
- ❌ Server administration beyond Omeka
- ❌ Complex database migrations requiring DBA expertise
- ❌ Custom server configurations unrelated to Omeka
- ❌ Third-party plugins not following Omeka standards

## Extending This Skill

To add your own custom patterns or organization-specific workflows:

1. **Add to examples/workflows.md**: Document your common workflows
2. **Update skill.md**: Add organization-specific configurations
3. **Create new files**: Add specialized guides in appropriate directories

Example:
```bash
# Add your custom workflow
echo "## Our Custom Item Import Process" >> examples/workflows.md
# Document your specific steps...
```

## Troubleshooting the Skill

If Claude Code isn't using the skill effectively:

1. **Check skill location**: Should be in `.claude/skills/omeka-s/skill.md`
2. **Verify file permissions**: Files should be readable
3. **Explicitly invoke**: Use `/skill omeka-s` command
4. **Provide context**: Mention you're working with Omeka S

## Version History

- **1.0.0** - Initial release
  - Complete theme development support
  - Full module development guide
  - Docker and traditional installation support
  - Comprehensive troubleshooting
  - Examples and quick reference

## Contributing

To improve this skill:

1. **Test workflows**: Try examples and report issues
2. **Add examples**: Document new patterns you discover
3. **Update references**: Keep official docs URLs current
4. **Share insights**: Add tips and best practices you learn

## Resources

### Official Documentation
- Omeka S Developer Docs: https://omeka.org/s/docs/developer/
- Omeka S User Manual: https://omeka.org/s/docs/user-manual/
- GitHub Repository: https://github.com/omeka/omeka-s
- Community Forum: https://forum.omeka.org/

### Skill Files
- **skill.md**: Comprehensive knowledge base
- **examples/workflows.md**: Step-by-step workflows
- **reference/quick-reference.md**: Quick command reference
- **README.md**: This usage guide

## Support

For issues with:
- **The skill itself**: Update/modify files in `.claude/skills/omeka-s/`
- **Omeka S**: Consult official docs and forum
- **Claude Code**: Visit https://claude.com/

## License

This skill documentation is provided as-is for use with Claude Code and Omeka S development. Omeka S is released under the GPL-3.0 license.

---

**Ready to develop with Omeka S?**

Just start a conversation with Claude Code about your Omeka S needs, and this skill will automatically provide expert guidance!

Examples to try:
- "Show me the current theme's CSS file"
- "Create a module that adds custom metadata"
- "Debug why my module isn't appearing"
- "Optimize image loading in my theme"
- "Change the site's accent color"
