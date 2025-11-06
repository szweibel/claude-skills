# Other Runes

## $bindable - Two-Way Binding

Marks a prop as bindable, allowing parent to use `bind:` directive.

### Basic Usage

```svelte
<!-- Input.svelte -->
<script>
	let { value = $bindable('') } = $props();
</script>

<input bind:value />
```

```svelte
<!-- Parent.svelte -->
<script>
	import Input from './Input.svelte';
	let text = $state('');
</script>

<Input bind:value={text} />
<p>You typed: {text}</p>
```

### With Fallback

```svelte
<script>
	let { value = $bindable('default text') } = $props();
</script>
```

Parent can omit `bind:`:
```svelte
<!-- Just passes value down (one-way) -->
<Input value="hello" />

<!-- Two-way binding -->
<Input bind:value={text} />
```

### Mutating Bindable Props

```svelte
<script>
	let { count = $bindable(0) } = $props();
</script>

<!-- ✅ OK to mutate bindable props -->
<button onclick={() => count++}>
	{count}
</button>
```

### Common Pattern: Custom Inputs

```svelte
<!-- Checkbox.svelte -->
<script>
	let { checked = $bindable(false), label } = $props();
</script>

<label>
	<input type="checkbox" bind:checked />
	{label}
</label>
```

```svelte
<!-- App.svelte -->
<script>
	let agreed = $state(false);
</script>

<Checkbox bind:checked={agreed} label="I agree to terms" />

<button disabled={!agreed}>Submit</button>
```

## $inspect - Debugging

Logs reactive state changes with stack traces (dev only).

### Basic Usage

```svelte
<script>
	let count = $state(0);
	let user = $state({ name: 'Ada' });

	$inspect(count); // Logs when count changes
	$inspect(count, user); // Logs when either changes
</script>
```

### Custom Handler

```svelte
<script>
	let count = $state(0);

	$inspect(count).with((type, value) => {
		if (type === 'init') {
			console.log('Initial value:', value);
		} else {
			console.log('Updated to:', value);
			debugger; // Break on changes
		}
	});
</script>
```

### Trace Function Execution

```svelte
<script>
	let count = $state(0);

	$effect(() => {
		// Logs which dependencies caused this to run
		$inspect.trace();

		console.log('Effect with count:', count);
	});
</script>
```

### With Label

```svelte
<script>
	$inspect.trace('My Effect Label');
</script>
```

### Production Behavior

`$inspect` becomes a no-op in production builds.

## $host - Custom Element Host

Access the host element in custom elements (web components).

### Basic Usage

```svelte
<!-- Counter.svelte -->
<svelte:options customElement="my-counter" />

<script>
	let count = $state(0);

	function increment() {
		count++;
		// Dispatch custom event
		$host().dispatchEvent(new CustomEvent('change', {
			detail: { count }
		}));
	}
</script>

<button onclick={increment}>
	Count: {count}
</button>
```

### Using the Custom Element

```svelte
<!-- App.svelte -->
<script>
	import './Counter.svelte';

	let total = $state(0);
</script>

<my-counter
	onchange={(e) => total = e.detail.count}
></my-counter>

<p>Total: {total}</p>
```

### Common Pattern: Forwarding Events

```svelte
<svelte:options customElement="my-button" />

<script>
	function handleClick(event) {
		// Forward event to host
		$host().dispatchEvent(new CustomEvent('clicked', {
			detail: { originalEvent: event }
		}));
	}
</script>

<button onclick={handleClick}>
	<slot></slot>
</button>
```

## Comparison: When to Use Each

| Rune | Use Case |
|------|----------|
| `$state` | Create reactive state |
| `$derived` | Compute values from state |
| `$effect` | Side effects (DOM, APIs) |
| `$props` | Accept component inputs |
| `$bindable` | Two-way binding on props |
| `$inspect` | Debug reactive values |
| `$host` | Custom element events |

## Common Patterns

### Bindable with Validation

```svelte
<script>
	let { value = $bindable(''), max = 10 } = $props();

	// Validate on change
	$effect(() => {
		if (value.length > max) {
			value = value.slice(0, max);
		}
	});
</script>

<input bind:value />
<p>{value.length}/{max}</p>
```

### Debug Effect Dependencies

```svelte
<script>
	let a = $state(1);
	let b = $state(2);
	let c = $state(3);

	$effect(() => {
		$inspect.trace('My Effect');
		console.log(a + b);
	});

	// Shows that only `a` and `b` are dependencies
</script>
```

### Custom Element with Slots

```svelte
<svelte:options customElement="my-card" />

<script>
	function close() {
		$host().dispatchEvent(new CustomEvent('close'));
	}
</script>

<div class="card">
	<slot name="header"></slot>
	<slot></slot>
	<button onclick={close}>Close</button>
</div>
```

## Best Practices

### $bindable

1. **Use sparingly** - Prefer one-way data flow
2. **Good for:** Form inputs, modals, drawers
3. **Bad for:** Complex data structures
4. **Always provide fallback** for optional bindables

### $inspect

1. **Remove before production** (or it's a no-op anyway)
2. **Use labels** for clarity
3. **Use `.with()` for breakpoints**
4. **Use `.trace()` to understand effects**

### $host

1. **Only for custom elements** - Errors elsewhere
2. **Dispatch semantic events** - Use clear event names
3. **Include detail** - Pass useful data in `event.detail`
4. **Document events** - Other devs need to know what's available

## Migration from Svelte 4

### bind:this

Still works! `bind:this` is not replaced by any rune.

```svelte
<script>
	let element;

	$effect(() => {
		if (element) {
			console.log(element.offsetHeight);
		}
	});
</script>

<div bind:this={element}>Content</div>
```

### Bindable Props

**Svelte 4:**
```svelte
<script>
	export let value;
</script>

<input bind:value />
```

**Svelte 5:**
```svelte
<script>
	let { value = $bindable() } = $props();
</script>

<input bind:value />
```

### Custom Events

**Svelte 4:**
```svelte
<script>
	import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();
</script>

<button onclick={() => dispatch('click', { data })}>
	Click
</button>
```

**Svelte 5 (regular components):**
```svelte
<script>
	let { onclick } = $props();
</script>

<button {onclick}>Click</button>
```

**Svelte 5 (custom elements):**
```svelte
<script>
	function handleClick() {
		$host().dispatchEvent(new CustomEvent('click', { detail: { data } }));
	}
</script>

<button onclick={handleClick}>Click</button>
```
