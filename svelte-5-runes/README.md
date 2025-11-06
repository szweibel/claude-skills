# Svelte 5 Runes - Claude Code Skill

A comprehensive Claude Code skill for Svelte 5's runes-based reactivity system. This skill provides AI assistants with patterns, best practices, and complete examples for all Svelte 5 runes.

## What This Skill Provides

This skill helps AI assistants write correct Svelte 5 code using:

- **$state** - Reactive state management (deep/shallow, classes, modules)
- **$derived** - Computed values with automatic dependencies
- **$effect** - Side effects and lifecycle management
- **$props** - Type-safe component props
- **$bindable** - Two-way data binding patterns
- **$inspect** - Debugging reactive values
- **$host** - Custom element integration
- **$props.id()** - Accessible component IDs

## Installation

### Option 1: Direct Clone

```bash
cd ~/.claude/skills/
git clone https://github.com/wiesson/svelte-5-runes
```

### Option 2: Manual Installation

1. Create the directory:
   ```bash
   mkdir -p ~/.claude/skills/svelte-5-runes
   ```

2. Download the skill files from this repository

3. Place them in `~/.claude/skills/svelte-5-runes/`

### Verify Installation

The skill should automatically activate when working with Svelte 5 projects or when code contains runes syntax (`$state`, `$derived`, etc.).

## Skill Structure

```
svelte-5-runes/
├── SKILL.md                    # Main entry point for AI (~450 lines)
├── README.md                   # This file (for humans)
└── references/
    ├── quick-reference.md      # All runes syntax at a glance
    ├── state.md               # $state deep dive
    ├── derived.md             # $derived patterns
    ├── effect.md              # $effect and side effects
    ├── props.md               # $props and component API
    └── other-runes.md         # $bindable, $inspect, $host
```

## What Makes This Skill Effective

### Optimized for AI Consumption

- **Right-sized**: Main file ~450 lines, references 200-300 lines each
- **Pattern-focused**: Complete working examples, not just API docs
- **Anti-patterns included**: Shows what NOT to do
- **Migration context**: Helps transition from Svelte 4

### Boosts Code Correctness

1. **Core patterns** - Reactive state, computed values, side effects
2. **Common pitfalls highlighted** - Infinite loops, missing cleanup, async tracking
3. **Best practices first** - Use `$derived`, not `$effect` for computed values
4. **Real workflow examples** - Forms, data fetching, timers, canvas
5. **Type safety emphasis** - TypeScript and JSDoc patterns

## Coverage

### All 8 Runes

- ✅ `$state` - Including deep/raw/snapshot/eager
- ✅ `$derived` - Including $derived.by and dependencies
- ✅ `$effect` - Including pre/tracking/pending/root
- ✅ `$props` - Including destructuring, defaults, rest props
- ✅ `$bindable` - Two-way binding patterns
- ✅ `$inspect` - Including .with() and .trace()
- ✅ `$host` - Custom element integration
- ✅ `$props.id()` - Component-scoped IDs

### Advanced Patterns

- ✅ Class-based state
- ✅ Deep vs shallow reactivity
- ✅ Effect cleanup and lifecycle
- ✅ Dependency tracking (sync/async)
- ✅ Module state sharing (.svelte.js)
- ✅ TypeScript type safety
- ✅ Optimistic updates
- ✅ Performance optimization

### Migration Guidance

- ✅ Svelte 4 → Svelte 5 patterns
- ✅ Reactive declarations → runes
- ✅ export let → $props
- ✅ createEventDispatcher → callbacks
- ✅ $: statements → $derived/$effect

## For AI Assistants

This skill is designed for Claude Code. The main content is in `SKILL.md`, organized as:

1. **What Are Runes** - Core concepts
2. **Quick Start Patterns** - Immediate implementation
3. **Common Workflows** - Real-world scenarios (forms, data fetching, classes)
4. **Best Practices** - Decision-making guidance
5. **Common Pitfalls** - What to avoid
6. **Migration Notes** - Svelte 4 → 5 changes
7. **References** - Links to detailed documentation

## Requirements

This skill assumes:
- Svelte 5.0+ project
- TypeScript (recommended but optional)
- Understanding of JavaScript proxies (helpful)
- Familiarity with basic Svelte concepts

## Key Differences from Svelte 4

| Svelte 4 | Svelte 5 |
|----------|----------|
| `let count = 0` | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `$: console.log(count)` | `$effect(() => console.log(count))` |
| `export let name` | `let { name } = $props()` |
| `export let value` (bindable) | `let { value = $bindable() } = $props()` |
| `createEventDispatcher()` | Callback props or `$host()` |

## Contributing

Contributions welcome! Please ensure:

1. Examples demonstrate best practices
2. Include both "do" and "don't" examples
3. Patterns are complete (not just fragments)
4. Code is tested in Svelte 5 playground
5. TypeScript examples include proper types

## Common Questions

**Q: When should I use `$effect` vs `$derived`?**
A: Use `$derived` for computed values. Use `$effect` only for side effects (DOM, APIs, analytics).

**Q: Why isn't my effect tracking a dependency?**
A: Dependencies must be read synchronously. Code after `await` won't track.

**Q: Can I export `$state` from a module?**
A: Only if you don't reassign it. Export an object with `$state` properties, or use getter functions.

**Q: How do I migrate from Svelte 4?**
A: See the Migration section in SKILL.md and the official [Svelte 5 migration guide](https://svelte.dev/docs/svelte/v5-migration-guide).

## License

MIT License - See LICENSE file for details

## Acknowledgments

Based on official Svelte 5 documentation from https://svelte.dev/docs/svelte

Special thanks to the Svelte team for creating an excellent reactivity system.
