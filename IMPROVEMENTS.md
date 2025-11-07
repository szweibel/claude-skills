# Skill Collection Improvement Plan

Based on Anthropic's best practices for agent skills, this document outlines needed improvements for each skill in the collection.

## Key Principles from Anthropic

1. **Progressive Disclosure**: Keep SKILL.md lean (<300 lines), move details to references/
2. **Bundled Resources**: Use scripts/ for deterministic code, references/ for documentation
3. **Clear Workflows**: Include decision trees and step-by-step guidance
4. **Focused Instructions**: Separate mutually exclusive contexts into distinct files
5. **Practical Examples**: Real-world usage patterns over theoretical documentation

## Skill-by-Skill Analysis

### 🔴 CRITICAL: claude-agent-ts-sdk (1185 lines → target: 300 lines)

**Issues:**
- Massively bloated SKILL.md with 1185 lines
- Too much detail in core file
- Mixes architecture patterns, tool docs, streaming, errors all together

**Improvements Needed:**
1. Create `references/patterns.md` - Move all 4 architecture patterns with full code
2. Create `references/tools.md` - Tool creation, composition, factories
3. Create `references/streaming.md` - Event handling and streaming patterns
4. Create `references/system-prompts.md` - How to write effective prompts
5. Create `references/project-setup.md` - Package.json, tsconfig, directory structure
6. Slim SKILL.md to:
   - Quick overview (50 lines)
   - When to use (20 lines)
   - Quick start example (50 lines)
   - Core concepts (50 lines)
   - Best practices summary (30 lines)
   - References section pointing to other files (20 lines)

**Files to Create:**
- `references/patterns.md` ✅ CREATED
- `references/tools.md`
- `references/streaming.md`
- `references/system-prompts.md`
- `references/project-setup.md`

### 🔴 CRITICAL: omeka-s (1381 lines → target: 400 lines)

**Issues:**
- Extremely long SKILL.md covering Docker, themes, modules, database
- No progressive disclosure
- Everything crammed into one file

**Improvements Needed:**
1. Create `references/docker-operations.md` - All Docker commands and file operations
2. Create `references/theme-development.md` - Theme structure, SCSS, templates
3. Create `references/module-development.md` - PHP module creation, events, forms
4. Create `references/database.md` - Database schema, queries, relationships
5. Create `references/troubleshooting.md` - Common issues and solutions
6. Slim SKILL.md to:
   - Overview of Omeka S (50 lines)
   - Installation type and context (50 lines)
   - Quick reference for Docker patterns (50 lines)
   - Development workflows (decision tree) (100 lines)
   - When to read each reference file (50 lines)
   - Common operations quick ref (100 lines)

### 🟡 MEDIUM: webapp-testing (96 lines → target: 150 lines)

**Issues:**
- Too minimal, lacks structure
- Decision tree exists but unclear
- Examples are referenced but not well integrated
- Missing common pitfalls section

**Improvements Needed:**
1. Expand decision tree with more clarity
2. Add "Common Pitfalls" section
3. Add "Troubleshooting" section
4. Better integrate examples with main workflow
5. Add references section:
   - `references/playwright-api.md` - Common Playwright patterns
   - `references/selectors.md` - How to find and use selectors effectively

### 🟡 MEDIUM: worldcat-api (209 lines → add references)

**Issues:**
- No bundled resources at all
- Good structure but could benefit from references
- Some content could move to references

**Improvements Needed:**
1. Create `references/api-endpoints.md` - Detailed API documentation
2. Create `references/examples.md` - Real-world usage examples
3. Move "Common Patterns" section to references
4. Keep SKILL.md focused on quick start and workflows

### 🟡 MEDIUM: xlsx (289 lines → add references)

**Issues:**
- No bundled resources
- Could benefit from references for complex operations

**Improvements Needed:**
1. Create `references/formulas.md` - Excel formula reference
2. Create `references/formatting.md` - Styling and formatting guide
3. Create `references/advanced.md` - Pivot tables, charts, macros
4. Keep SKILL.md focused on common operations

### 🟢 GOOD: pdf (295 lines + 8 scripts)

**Status:** Good progressive disclosure with scripts

**Minor Improvements:**
1. Create `references/advanced-operations.md` - Move some advanced content
2. Add `references/forms-reference.md` - Detailed form field documentation
3. Keep current structure mostly intact

### 🟢 GOOD: svelte-5-runes (569 lines + 6 references)

**Status:** Good structure with references directory

**Minor Improvements:**
1. Slim SKILL.md to ~300 lines by moving more to references
2. Add `references/migration-guide.md` - Svelte 4 to 5 migration
3. Add decision tree for which rune to use when

### 🟢 GOOD: skill-creator (210 lines + 3 scripts)

**Status:** Good foundation with helpful scripts

**Minor Improvements:**
1. Add `references/skill-examples.md` - Analysis of good skills
2. Add `references/anti-patterns.md` - Common mistakes to avoid
3. Add more examples to assets/

### 🟢 GOOD: docx (197 lines + scripts)

**Status:** Reasonable length with script support

**Minor Improvements:**
1. Create `references/ooxml-spec.md` - Move OOXML details
2. Add `references/advanced-formatting.md` - Complex formatting patterns
3. Keep current structure

### 🟢 GOOD: pptx (484 lines + scripts)

**Status:** Could be slightly leaner but reasonable

**Minor Improvements:**
1. Create `references/layouts.md` - Slide layout patterns
2. Create `references/animations.md` - Animation and transition docs
3. Slim SKILL.md to ~350 lines

## Priority Implementation Order

### Phase 1: Critical Bloat Fixes (HIGH IMPACT)
1. **claude-agent-ts-sdk** - Reduce 1185 → 300 lines
2. **omeka-s** - Reduce 1381 → 400 lines

### Phase 2: Missing Structure (MEDIUM IMPACT)
3. **webapp-testing** - Enhance 96 → 150 lines
4. **worldcat-api** - Add references/
5. **xlsx** - Add references/

### Phase 3: Polish (LOW IMPACT)
6. **svelte-5-runes** - Slim 569 → 300 lines
7. **pptx** - Slim 484 → 350 lines
8. Add reference files to remaining skills

## Measurement of Success

- **Before**: Average skill size: 561 lines
- **After Target**: Average skill size: 300 lines
- **Before**: 3/10 skills have references/
- **After Target**: 10/10 skills have references/
- **Before**: Variable structure across skills
- **After Target**: Consistent progressive disclosure pattern

## Next Steps

1. Start with claude-agent-ts-sdk (biggest impact)
2. Move to omeka-s (second biggest impact)
3. Then enhance smaller skills systematically
4. Document the improved pattern in skill-creator
5. Commit improvements incrementally
