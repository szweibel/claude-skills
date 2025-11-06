# Quick Reference

All Svelte 5 runes with copy-paste examples.

## $state

```svelte
<script>
	// Primitive
	let count = $state(0);

	// Object (deep reactive)
	let user = $state({ name: 'Ada', age: 28 });

	// Array (deep reactive)
	let items = $state([1, 2, 3]);

	// Raw (not deep reactive)
	let config = $state.raw({ api: 'https://api.com' });

	// Class field
	class Counter {
		count = $state(0);
	}
</script>

<button onclick={() => count++}>{count}</button>
<button onclick={() => user.age++}>{user.name}: {user.age}</button>
<button onclick={() => items.push(4)}>{items.length} items</button>
```

## $state.snapshot

```svelte
<script>
	let obj = $state({ count: 0 });

	function logSnapshot() {
		// Converts proxy to plain object
		console.log($state.snapshot(obj));
	}
</script>
```

## $derived

```svelte
<script>
	let count = $state(0);

	// Simple expression
	let doubled = $derived(count * 2);

	// Complex computation
	let status = $derived.by(() => {
		if (count < 5) return 'low';
		if (count < 10) return 'medium';
		return 'high';
	});

	// From array
	let items = $state([1, 2, 3, 4, 5]);
	let evens = $derived(items.filter(n => n % 2 === 0));
	let sum = $derived(items.reduce((a, b) => a + b, 0));
</script>

<p>{count} * 2 = {doubled}</p>
<p>Status: {status}</p>
<p>Evens: {evens.join(', ')}</p>
<p>Sum: {sum}</p>
```

## $effect

```svelte
<script>
	let count = $state(0);

	// Basic effect
	$effect(() => {
		console.log('Count is:', count);
	});

	// With cleanup
	$effect(() => {
		const interval = setInterval(() => count++, 1000);

		return () => clearInterval(interval);
	});

	// Pre-effect (runs before DOM updates)
	let div;
	$effect.pre(() => {
		if (div) {
			console.log('Before update, height:', div.offsetHeight);
		}
	});

	// Check if tracking
	console.log($effect.tracking()); // false in setup, true in template

	// Check pending promises
	if ($effect.pending()) {
		console.log('Promises pending:', $effect.pending());
	}
</script>

<div bind:this={div}>Content</div>
```

## $props

```svelte
<!-- Child.svelte -->
<script>
	// All props
	let props = $props();

	// Destructured
	let { name, age } = $props();

	// With defaults
	let { name, age = 18 } = $props();

	// Renamed
	let { class: className } = $props();

	// Rest props
	let { name, age, ...rest } = $props();

	// TypeScript
	interface Props {
		name: string;
		age?: number;
	}
	let { name, age = 18 }: Props = $props();
</script>

<p>{name} is {age} years old</p>
<div {...rest}></div>
```

```svelte
<!-- Parent.svelte -->
<Child name="Ada" age={28} />
```

## $props.id()

```svelte
<script>
	const uid = $props.id();
</script>

<label for="{uid}-name">Name:</label>
<input id="{uid}-name" type="text" />

<label for="{uid}-email">Email:</label>
<input id="{uid}-email" type="email" />
```

## $bindable

```svelte
<!-- Input.svelte -->
<script>
	let { value = $bindable('') } = $props();
</script>

<input bind:value />
```

```svelte
<!-- App.svelte -->
<script>
	import Input from './Input.svelte';
	let text = $state('');
</script>

<Input bind:value={text} />
<p>You typed: {text}</p>
```

## $inspect

```svelte
<script>
	let count = $state(0);
	let user = $state({ name: 'Ada' });

	// Log when changes
	$inspect(count);

	// Log multiple values
	$inspect(count, user);

	// Custom handler
	$inspect(count).with((type, value) => {
		if (type === 'init') {
			console.log('Initial:', value);
		} else {
			console.log('Updated:', value);
		}
	});

	// Trace function calls
	$effect(() => {
		$inspect.trace();
		console.log('Effect ran with count:', count);
	});
</script>
```

## $host

```svelte
<!-- For custom elements only -->
<svelte:options customElement="my-button" />

<script>
	function handleClick() {
		$host().dispatchEvent(new CustomEvent('clicked'));
	}
</script>

<button onclick={handleClick}>
	Click me
</button>
```

## Common Patterns

### Form State

```svelte
<script>
	let form = $state({
		email: '',
		password: '',
		remember: false
	});

	let errors = $derived.by(() => {
		const e = {};
		if (!form.email.includes('@')) e.email = 'Invalid email';
		if (form.password.length < 8) e.password = 'Too short';
		return e;
	});

	let isValid = $derived(Object.keys(errors).length === 0);
</script>

<input bind:value={form.email} type="email" />
{#if errors.email}<span class="error">{errors.email}</span>{/if}

<input bind:value={form.password} type="password" />
{#if errors.password}<span class="error">{errors.password}</span>{/if}

<label>
	<input bind:checked={form.remember} type="checkbox" />
	Remember me
</label>

<button disabled={!isValid}>Submit</button>
```

### Todo List

```svelte
<script>
	let todos = $state([
		{ id: 1, text: 'Learn Svelte 5', done: false },
		{ id: 2, text: 'Build an app', done: false }
	]);

	let filter = $state('all');

	let filteredTodos = $derived(
		filter === 'all' ? todos :
		filter === 'active' ? todos.filter(t => !t.done) :
		todos.filter(t => t.done)
	);

	let remaining = $derived(todos.filter(t => !t.done).length);

	function addTodo(text) {
		todos.push({
			id: Date.now(),
			text,
			done: false
		});
	}

	function toggleTodo(id) {
		const todo = todos.find(t => t.id === id);
		if (todo) todo.done = !todo.done;
	}

	function removeTodo(id) {
		todos = todos.filter(t => t.id !== id);
	}
</script>

{#each filteredTodos as todo}
	<div>
		<input
			type="checkbox"
			checked={todo.done}
			onchange={() => toggleTodo(todo.id)}
		/>
		<span>{todo.text}</span>
		<button onclick={() => removeTodo(todo.id)}>×</button>
	</div>
{/each}

<p>{remaining} remaining</p>

<button onclick={() => filter = 'all'}>All</button>
<button onclick={() => filter = 'active'}>Active</button>
<button onclick={() => filter = 'completed'}>Completed</button>
```

### Timer

```svelte
<script>
	let seconds = $state(0);
	let running = $state(false);

	$effect(() => {
		if (!running) return;

		const interval = setInterval(() => {
			seconds++;
		}, 1000);

		return () => clearInterval(interval);
	});

	function toggle() {
		running = !running;
	}

	function reset() {
		seconds = 0;
		running = false;
	}
</script>

<h1>{seconds}s</h1>
<button onclick={toggle}>{running ? 'Pause' : 'Start'}</button>
<button onclick={reset}>Reset</button>
```

### Data Fetching

```svelte
<script>
	let userId = $state(1);
	let data = $state(null);
	let loading = $state(false);
	let error = $state(null);

	async function fetchUser(id) {
		loading = true;
		error = null;

		try {
			const res = await fetch(`https://api.example.com/users/${id}`);
			data = await res.json();
		} catch (e) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		fetchUser(userId);
	});
</script>

{#if loading}
	<p>Loading...</p>
{:else if error}
	<p class="error">{error}</p>
{:else if data}
	<div>
		<h2>{data.name}</h2>
		<p>{data.email}</p>
	</div>
{/if}

<button onclick={() => userId++}>Next User</button>
```

### Canvas Drawing

```svelte
<script>
	let canvas;
	let color = $state('#ff3e00');
	let size = $state(50);

	$effect(() => {
		if (!canvas) return;

		const ctx = canvas.getContext('2d');
		ctx.clearRect(0, 0, canvas.width, canvas.height);

		ctx.fillStyle = color;
		ctx.fillRect(0, 0, size, size);
	});
</script>

<canvas bind:this={canvas} width="200" height="200"></canvas>

<input bind:value={color} type="color" />
<input bind:value={size} type="range" min="10" max="200" />
```

### Shared State (`.svelte.js`)

```js
// store.svelte.js
export const count = $state(0);

export function increment() {
	count++;
}

// Or with object
export const state = $state({
	count: 0,
	user: null
});

export function setUser(user) {
	state.user = user;
}
```

```svelte
<!-- App.svelte -->
<script>
	import { count, increment } from './store.svelte.js';
</script>

<button onclick={increment}>
	Count: {count}
</button>
```
