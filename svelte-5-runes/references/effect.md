# $effect - Side Effects

Effects run when state changes. Use for DOM manipulation, third-party libraries, analytics, network requests.

## Basic Usage

```svelte
<script>
	let count = $state(0);

	$effect(() => {
		console.log(`Count is now: ${count}`);
	});
</script>
```

Effects track dependencies automatically and re-run when they change.

## Lifecycle

Effects run:
1. **After** component mounts to DOM
2. In a **microtask** after state changes
3. Re-runs are **batched**

```svelte
<script>
	let color = $state('#ff3e00');
	let size = $state(50);

	$effect(() => {
		// Runs once on mount, then whenever color OR size changes
		// Changing both in same moment = single re-run
	});
</script>
```

## Cleanup Functions

Return a function to clean up subscriptions/intervals:

```svelte
<script>
	let seconds = $state(0);

	$effect(() => {
		const interval = setInterval(() => seconds++, 1000);

		return () => {
			clearInterval(interval); // Runs before re-run or unmount
		};
	});
</script>
```

## Dependencies

Dependencies are read **synchronously**:

```svelte
<script>
	let userId = $state(1);
	let data = $state(null);

	$effect(() => {
		// `userId` IS tracked (read before await)
		const id = userId;

		fetch(`/api/users/${id}`)
			.then(r => r.json())
			.then(result => {
				// This runs async - any state read here is NOT tracked
				data = result;
			});
	});
</script>
```

## $effect.pre

Runs **before** DOM updates (rare):

```svelte
<script>
	let div;
	let messages = $state([]);

	$effect.pre(() => {
		if (!div) return;

		messages.length; // Track length

		// Check before DOM updates
		if (div.offsetHeight + div.scrollTop > div.scrollHeight - 20) {
			tick().then(() => div.scrollTo(0, div.scrollHeight));
		}
	});
</script>

<div bind:this={div}>
	{#each messages as message}
		<p>{message}</p>
	{/each}
</div>
```

## $effect.tracking

Check if code is in tracking context:

```svelte
<script>
	console.log($effect.tracking()); // false (in setup)

	$effect(() => {
		console.log($effect.tracking()); // true
	});
</script>

<p>{$effect.tracking()}</p> <!-- true (in template) -->
```

## $effect.pending

Returns count of pending promises in current [boundary](https://svelte.dev/docs/svelte/svelte-boundary):

```svelte
<script>
	let a = $state(0);
	let b = $state(0);

	async function add(x, y) {
		await new Promise(r => setTimeout(r, 1000));
		return x + y;
	}
</script>

<p>{a} + {b} = {await add(a, b)}</p>

{#if $effect.pending()}
	<p>Calculating... ({$effect.pending()} pending)</p>
{/if}
```

## $effect.root

Create non-tracked scope with manual cleanup (advanced):

```svelte
<script>
	function createLogger() {
		const destroy = $effect.root(() => {
			$effect(() => {
				console.log('Effect inside root');
			});

			return () => {
				console.log('Cleanup');
			};
		});

		return destroy;
	}

	let cleanup = createLogger();

	// Later...
	cleanup();
</script>
```

## When NOT to Use $effect

### ❌ Synchronizing State

**Don't:**
```svelte
<script>
	let count = $state(0);
	let doubled = $state(0);

	$effect(() => {
		doubled = count * 2;
	});
</script>
```

**Do:**
```svelte
<script>
	let count = $state(0);
	let doubled = $derived(count * 2);
</script>
```

### ❌ Computing Values

**Don't:**
```svelte
<script>
	let items = $state([1, 2, 3]);
	let sum = $state(0);

	$effect(() => {
		sum = items.reduce((a, b) => a + b, 0);
	});
</script>
```

**Do:**
```svelte
<script>
	let items = $state([1, 2, 3]);
	let sum = $derived(items.reduce((a, b) => a + b, 0));
</script>
```

### ❌ Event Handlers

**Don't:**
```svelte
<script>
	let count = $state(0);

	$effect(() => {
		// Re-runs on every count change!
		document.addEventListener('click', () => count++);
	});
</script>
```

**Do:**
```svelte
<script>
	let count = $state(0);
</script>

<svelte:document onclick={() => count++} />
```

## Common Patterns

### Canvas Drawing

```svelte
<script>
	let canvas;
	let color = $state('#ff3e00');

	$effect(() => {
		if (!canvas) return;

		const ctx = canvas.getContext('2d');
		ctx.fillStyle = color;
		ctx.fillRect(0, 0, 100, 100);
	});
</script>

<canvas bind:this={canvas} width="100" height="100"></canvas>
```

### Third-Party Library

```svelte
<script>
	import confetti from 'canvas-confetti';

	let celebrate = $state(false);

	$effect(() => {
		if (celebrate) {
			confetti();
		}
	});
</script>
```

### Local Storage Sync

```svelte
<script>
	let theme = $state(localStorage.getItem('theme') || 'light');

	$effect(() => {
		localStorage.setItem('theme', theme);
		document.body.className = theme;
	});
</script>
```

### Analytics

```svelte
<script>
	let page = $state('/');

	$effect(() => {
		analytics.track('pageview', { path: page });
	});
</script>
```

## Common Pitfalls

### Infinite Loops

```svelte
<script>
	let count = $state(0);

	// ❌ Infinite loop!
	$effect(() => {
		count++; // Reads and writes count
	});

	// ✅ Use untrack if you must
	import { untrack } from 'svelte';

	$effect(() => {
		const current = untrack(() => count);
		count = current + 1; // Still bad, but won't loop
	});
</script>
```

### Missing Cleanup

```svelte
<script>
	// ❌ Interval never cleared
	$effect(() => {
		setInterval(() => console.log('tick'), 1000);
	});

	// ✅ Return cleanup function
	$effect(() => {
		const id = setInterval(() => console.log('tick'), 1000);
		return () => clearInterval(id);
	});
</script>
```

### Reading Async State

```svelte
<script>
	let userId = $state(1);

	$effect(() => {
		fetch(`/api/users/${userId}`)
			.then(r => r.json())
			.then(data => {
				// Any state read here is NOT tracked!
			});
	});

	// ✅ Read userId before async
	$effect(() => {
		const id = userId; // Tracked
		fetch(`/api/users/${id}`) // ...
	});
</script>
```

## Best Practices

1. **Use `$derived` for computed values, not `$effect`**
2. **Always cleanup** subscriptions/intervals/listeners
3. **Read dependencies before `await`** to track them
4. **Avoid reading and writing same state** (infinite loops)
5. **Check for null** when using `bind:this`
6. **Use `$effect.pre` sparingly** - only for pre-DOM checks
7. **Prefer declarative patterns** over imperative effects
