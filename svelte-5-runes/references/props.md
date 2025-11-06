# $props - Component Props

The `$props` rune defines component inputs. Props flow from parent to child.

## Basic Usage

```svelte
<!-- Child.svelte -->
<script>
	let props = $props();
</script>

<p>Name: {props.name}</p>
<p>Age: {props.age}</p>
```

```svelte
<!-- Parent.svelte -->
<Child name="Ada" age={28} />
```

## Destructuring (Recommended)

```svelte
<script>
	let { name, age } = $props();
</script>

<p>{name} is {age} years old</p>
```

## Fallback Values

```svelte
<script>
	let { name, age = 18 } = $props();
</script>
```

Parent can omit `age`:
```svelte
<Child name="Ada" /> <!-- age defaults to 18 -->
```

## Renaming Props

Useful for reserved words or invalid identifiers:

```svelte
<script>
	let { class: className, super: trouper } = $props();
</script>

<div class={className}>{trouper}</div>
```

## Rest Props

```svelte
<script>
	let { name, age, ...rest } = $props();
</script>

<p>{name}, {age}</p>
<div {...rest}></div> <!-- Spreads remaining props -->
```

Usage:
```svelte
<Child name="Ada" age={28} class="highlight" data-id="123" />
<!-- rest = { class: "highlight", data-id: "123" } -->
```

## Type Safety (TypeScript)

```svelte
<script lang="ts">
	interface Props {
		name: string;
		age?: number;
		onUpdate?: (value: string) => void;
	}

	let { name, age = 18, onUpdate }: Props = $props();
</script>
```

## Type Safety (JSDoc)

```svelte
<script>
	/** @type {{ name: string, age?: number }} */
	let { name, age = 18 } = $props();
</script>
```

## $props.id()

Generate component-scoped IDs (consistent between server/client):

```svelte
<script>
	const uid = $props.id();
</script>

<label for="{uid}-email">Email:</label>
<input id="{uid}-email" type="email" />

<label for="{uid}-password">Password:</label>
<input id="{uid}-password" type="password" />
```

## Updating Props

Props can be temporarily overridden (e.g., optimistic UI):

```svelte
<!-- Child.svelte -->
<script>
	let { count } = $props();
</script>

<button onclick={() => count++}>
	{count}
</button>
```

Clicking increments `count` in child, but parent's value isn't affected. When parent's `count` changes, child's override is replaced.

**Caution:** Don't mutate props unless they're [$bindable]($bindable).

## Props Flow

Props are **pass-by-value**. You get the _current value_, not a reference:

```svelte
<!-- Parent.svelte -->
<script>
	let count = $state(0);
</script>

<Child {count} />
<button onclick={() => count++}>Parent: {count}</button>
```

```svelte
<!-- Child.svelte -->
<script>
	let { count } = $props();

	// `count` is the value at time of render
	// Doesn't stay in sync with parent automatically
</script>

<p>Child sees: {count}</p>
```

## Callback Props

For child-to-parent communication:

```svelte
<!-- Child.svelte -->
<script>
	let { onIncrement } = $props();
</script>

<button onclick={onIncrement}>Increment</button>
```

```svelte
<!-- Parent.svelte -->
<script>
	let count = $state(0);
</script>

<Child onIncrement={() => count++} />
<p>Count: {count}</p>
```

## Fallback Values and Reactivity

**Important:** Fallback values are NOT reactive proxies:

```svelte
<script>
	let { items = [1, 2, 3] } = $props();

	// ❌ If fallback is used, mutation has no effect
	items.push(4);

	// ✅ Reassignment works
	items = [...items, 4];
</script>
```

If parent passes `items`, it will be reactive. If fallback is used, it won't be.

## Exporting State from Modules

Cannot directly export `$state` that will be reassigned:

```js
// ❌ Doesn't work
// state.svelte.js
export let count = $state(0);
```

**Solution 1:** Export object:
```js
// ✅ Works
export const state = $state({ count: 0 });
```

**Solution 2:** Use getters:
```js
// ✅ Works
let count = $state(0);

export function getCount() {
	return count;
}

export function setCount(value) {
	count = value;
}
```

## Common Patterns

### Required vs Optional

```svelte
<script lang="ts">
	interface Props {
		// Required
		name: string;

		// Optional with default
		age?: number;

		// Optional without default
		email?: string;
	}

	let { name, age = 18, email }: Props = $props();
</script>

{#if email}
	<p>Email: {email}</p>
{/if}
```

### Prop Validation (Runtime)

```svelte
<script>
	let { age } = $props();

	$effect(() => {
		if (age < 0 || age > 150) {
			console.warn('Invalid age:', age);
		}
	});
</script>
```

### Component Wrappers

```svelte
<!-- Button.svelte -->
<script>
	let { class: className, children, ...rest } = $props();
</script>

<button class="btn {className}" {...rest}>
	{@render children?.()}
</button>
```

```svelte
<!-- Usage -->
<Button class="primary" onclick={() => alert('hi')}>
	Click me
</Button>
```

## Common Pitfalls

### Mutating Props

```svelte
<!-- Child.svelte -->
<script>
	let { user } = $props();
</script>

<!-- ❌ Don't mutate props -->
<button onclick={() => user.name = 'New'}>
	Change name
</button>

<!-- ✅ Use callback instead -->
<script>
	let { user, onUpdate } = $props();
</script>

<button onclick={() => onUpdate({ ...user, name: 'New' })}>
	Change name
</button>
```

### Destructuring Breaks Updates

```svelte
<script>
	let { user } = $props();

	// ❌ `name` won't update when user.name changes
	let { name } = user;
</script>

<!-- ✅ Access directly -->
<p>{user.name}</p>
```

### Fallback Reactivity

```svelte
<script>
	// If parent doesn't pass `items`, fallback is NOT reactive
	let { items = [] } = $props();

	// ❌ No effect if fallback used
	items.push(1);

	// ✅ Always works
	items = [...items, 1];
</script>
```

## Best Practices

1. **Use destructuring** for cleaner code
2. **Provide defaults** for optional props
3. **Use TypeScript/JSDoc** for type safety
4. **Don't mutate props** (use `$bindable` or callbacks)
5. **Use callback props** for child → parent communication
6. **Validate at runtime** if needed
7. **Use $props.id()** for accessible form controls
