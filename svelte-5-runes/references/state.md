# $state - Reactive State

The `$state` rune creates reactive state that triggers UI updates when changed.

## Basic Usage

```svelte
<script>
	let count = $state(0);
</script>

<button onclick={() => count++}>
	Clicks: {count}
</button>
```

`count` is just a number — you update it like any variable, and Svelte updates the UI automatically.

## Deep Reactivity

Objects and arrays become **deeply reactive proxies**:

```svelte
<script>
	let user = $state({
		name: 'Ada',
		address: {
			city: 'London',
			zip: 'SW1A 1AA'
		}
	});

	let items = $state([1, 2, 3]);
</script>

<button onclick={() => user.address.city = 'Paris'}>
	Move to Paris
</button>

<button onclick={() => items.push(items.length + 1)}>
	Add item
</button>
```

**How it works:**
- Svelte wraps objects/arrays in [Proxies](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Proxy)
- Proxy intercepts property access and modifications
- Updates are granular — only affected parts re-render
- Proxification is recursive until non-plain objects are found

## Destructuring Breaks Reactivity

```svelte
<script>
	let todos = $state([
		{ done: false, text: 'learn svelte' }
	]);

	// ❌ `done` is not reactive
	let { done, text } = todos[0];

	todos[0].done = true; // UI won't update for `done`

	// ✅ Access properties directly
	todos[0].done = true; // UI updates
</script>
```

## Classes with $state

Use `$state` in class fields (public/private) or first assignment in constructor:

```svelte
<script>
	class Todo {
		done = $state(false);
		#text = $state('');

		constructor(text) {
			this.text = $state(text);
		}

		toggle = () => {
			this.done = !this.done;
		}

		reset() {
			this.done = false;
			this.text = '';
		}
	}

	let todo = new Todo('Learn runes');
</script>

<label>
	<input type="checkbox" checked={todo.done} onchange={todo.toggle} />
	{todo.text}
</label>

<!-- ⚠️ This won't work - `this` context issue -->
<button onclick={todo.reset}>Reset</button>

<!-- ✅ Use arrow function or inline -->
<button onclick={() => todo.reset()}>Reset</button>
```

**Note:** Properties become get/set methods (not enumerable).

## $state.raw - Shallow Reactivity

For data you won't mutate, or large objects where deep reactivity is expensive:

```svelte
<script>
	let config = $state.raw({
		apiUrl: 'https://api.example.com',
		timeout: 5000,
		headers: { /* hundreds of properties */ }
	});

	// ❌ Mutation has no effect
	config.timeout = 10000;

	// ✅ Reassignment works
	config = {
		...config,
		timeout: 10000
	};
</script>
```

**When to use:**
- Large configuration objects
- Immutable data patterns
- Performance optimization
- Data you'll replace, not mutate

**Note:** `$state.raw` can _contain_ reactive state (e.g., array of reactive objects).

## $state.snapshot - Get Plain Object

Convert reactive proxy to plain JavaScript object:

```svelte
<script>
	let counter = $state({ count: 0 });

	function logSnapshot() {
		// Logs `{ count: 0 }` instead of `Proxy { ... }`
		console.log($state.snapshot(counter));

		// Useful for external APIs
		structuredClone($state.snapshot(counter));
		localStorage.setItem('counter', JSON.stringify($state.snapshot(counter)));
	}
</script>
```

**Use cases:**
- Logging without proxy noise
- External libraries that don't handle proxies
- `structuredClone`, `JSON.stringify`, etc.

## $state.eager - Immediate UI Updates

By default, state changes inside `await` expressions delay UI updates ([synchronized updates](https://svelte.dev/docs/svelte/await-expressions#Synchronized-updates)).

Use `$state.eager()` to update UI immediately:

```svelte
<script>
	let pathname = $state('/');
</script>

<nav>
	<a
		href="/"
		aria-current={$state.eager(pathname) === '/' ? 'page' : null}
		onclick={() => pathname = '/'}
	>
		Home
	</a>
	<a
		href="/about"
		aria-current={$state.eager(pathname) === '/about' ? 'page' : null}
		onclick={() => pathname = '/about'}
	>
		About
	</a>
</nav>
```

**Use sparingly** — only for immediate user feedback during async operations.

## Passing State to Functions

JavaScript is **pass-by-value**. When you pass state to functions, you pass the _value_, not the _variable_:

```svelte
<script>
	let a = $state(1);
	let b = $state(2);

	// ❌ Gets current values, not reactive
	function add(x, y) {
		return x + y;
	}

	let total = add(a, b); // 3
	a = 10; // total is still 3!

	// ✅ Use derived instead
	let total = $derived(a + b); // Always current

	// Or pass getters
	function add(getA, getB) {
		return () => getA() + getB();
	}

	let total = add(() => a, () => b);
	console.log(total()); // Always current
</script>
```

## Sharing State Between Modules

You **cannot directly export** state that will be reassigned:

```js
// ❌ This doesn't work
// state.svelte.js
export let count = $state(0);

export function increment() {
	count += 1; // Other files won't see this
}
```

**Solution 1:** Export object (mutations work):

```js
// ✅ Works - we mutate, not reassign
// state.svelte.js
export const counter = $state({
	count: 0
});

export function increment() {
	counter.count += 1;
}
```

```svelte
<!-- App.svelte -->
<script>
	import { counter, increment } from './state.svelte.js';
</script>

<button onclick={increment}>
	{counter.count}
</button>
```

**Solution 2:** Use getter functions:

```js
// ✅ Works - export functions
// state.svelte.js
let count = $state(0);

export function getCount() {
	return count;
}

export function increment() {
	count += 1;
}
```

```svelte
<!-- App.svelte -->
<script>
	import { getCount, increment } from './state.svelte.js';
</script>

<button onclick={increment}>
	{getCount()}
</button>
```

## Built-In Reactive Classes

Svelte provides reactive versions of built-in classes in `svelte/reactivity`:

```svelte
<script>
	import { SvelteSet, SvelteMap, SvelteDate, SvelteURL } from 'svelte/reactivity';

	let items = new SvelteSet([1, 2, 3]);
	let users = new SvelteMap();
	let now = new SvelteDate();
	let url = new SvelteURL('https://example.com');

	// These trigger reactivity
	items.add(4);
	users.set('ada', { name: 'Ada Lovelace' });
	now.setHours(12);
	url.searchParams.set('page', '2');
</script>
```

## Performance Tips

1. **Use `$state.raw` for immutable data**
   ```js
   let config = $state.raw(largeConfigObject);
   ```

2. **Avoid unnecessary deep proxies**
   ```js
   // If you only care about array length, not items
   let items = $state.raw([...]);
   let count = $derived(items.length);
   ```

3. **Class instances aren't proxied**
   ```js
   class Point {
		x = $state(0);
		y = $state(0);
	}
	let point = new Point(); // Only x/y are reactive, not the Point instance
   ```

## Common Pitfalls

### Mutation vs Reassignment

```svelte
<script>
	let items = $state([1, 2, 3]);

	// ✅ Mutation - works
	items.push(4);
	items[0] = 10;
	items.splice(1, 1);

	// ✅ Reassignment - works
	items = [...items, 4];
	items = items.filter(x => x > 1);

	// With $state.raw:
	let raw = $state.raw([1, 2, 3]);

	// ❌ Mutation - no effect
	raw.push(4);

	// ✅ Reassignment - works
	raw = [...raw, 4];
</script>
```

### Console Logging Proxies

```svelte
<script>
	let obj = $state({ count: 0 });

	console.log(obj); // Proxy { ... } (confusing)
	console.log($state.snapshot(obj)); // { count: 0 } (clear)
</script>
```

### Class Method `this` Binding

```svelte
<script>
	class Counter {
		count = $state(0);

		increment() {
			this.count++; // `this` might not be Counter instance
		}

		// ✅ Use arrow function
		increment = () => {
			this.count++;
		}
	}

	let counter = new Counter();
</script>

<!-- ❌ `this` will be the button -->
<button onclick={counter.increment}>+</button>

<!-- ✅ Use inline function -->
<button onclick={() => counter.increment()}>+</button>
```
