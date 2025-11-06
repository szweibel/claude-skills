# $derived - Computed Values

The `$derived` rune creates values computed from reactive state. Automatically recalculates when dependencies change.

## Basic Usage

```svelte
<script>
	let count = $state(0);
	let doubled = $derived(count * 2);
</script>

<button onclick={() => count++}>
	{count} × 2 = {doubled}
</button>
```

**Key point:** Without `$derived`, `doubled` would only calculate once and never update.

## Complex Derivations with $derived.by

For multi-line calculations, use `$derived.by` with a function:

```svelte
<script>
	let numbers = $state([1, 2, 3, 4, 5]);

	let stats = $derived.by(() => {
		let total = 0;
		let count = numbers.length;

		for (const n of numbers) {
			total += n;
		}

		return {
			sum: total,
			average: total / count,
			max: Math.max(...numbers),
			min: Math.min(...numbers)
		};
	});
</script>

<p>Sum: {stats.sum}</p>
<p>Average: {stats.average}</p>
<p>Range: {stats.min} - {stats.max}</p>
```

**Note:** `$derived(expression)` is equivalent to `$derived.by(() => expression)`.

## Understanding Dependencies

Dependencies are anything read **synchronously** inside the derived expression:

```svelte
<script>
	let a = $state(1);
	let b = $state(2);
	let c = $state(3);

	// Only depends on `a` and `b`
	let sum = $derived(a + b);

	// `c` is never read, so changes to `c` don't trigger recalculation
</script>
```

### Conditional Dependencies

Dependencies can change based on execution path:

```svelte
<script>
	let condition = $state(true);
	let x = $state(1);
	let y = $state(2);

	let result = $derived(condition ? x : y);

	// When condition is true: depends on `condition` and `x`
	// When condition is false: depends on `condition` and `y`
</script>
```

### Async Code Doesn't Track

```svelte
<script>
	let userId = $state(1);

	// ❌ userId after `await` is NOT tracked
	let user = $derived.by(async () => {
		const response = await fetch(`/api/users/${userId}`);
		return response.json();
	});

	// ✅ Read before await to track
	let user = $derived.by(async () => {
		const id = userId; // Tracked!
		const response = await fetch(`/api/users/${id}`);
		return response.json();
	});
</script>
```

## Excluding Dependencies with untrack

Use [`untrack`](https://svelte.dev/docs/svelte#untrack) to read state without creating a dependency:

```svelte
<script>
	import { untrack } from 'svelte';

	let count = $state(0);
	let doubled = $state(0);

	// Only depends on `count`, not `doubled`
	let result = $derived.by(() => {
		const current = untrack(() => doubled);
		return count + current;
	});
</script>
```

## Overriding Derived Values

Since Svelte 5.25, you can temporarily override derived values (e.g., for optimistic UI):

```svelte
<script>
	let { post, like } = $props();

	let likes = $derived(post.likes);

	async function onclick() {
		// Immediately show incremented value
		likes += 1;

		try {
			await like(); // Update server
		} catch {
			// Revert on error
			likes -= 1;
		}
	}
</script>

<button {onclick}>🧡 {likes}</button>
```

**How it works:**
- Reassignment temporarily overrides the derived value
- When `post.likes` changes, the derived recalculates and replaces your override
- Perfect for optimistic updates

## Deriveds and Reactivity

Unlike `$state`, `$derived` values are **not converted to deep proxies**:

```svelte
<script>
	let items = $state([{ name: 'A' }, { name: 'B' }]);

	// `firstItem` is the actual object, not a proxy wrapper
	let firstItem = $derived(items[0]);

	// ✅ Mutations affect the underlying `items` array
	firstItem.name = 'Updated';
</script>
```

If `items` was _not_ deeply reactive, mutating `firstItem` would have no effect.

## Destructuring Deriveds

Destructuring makes all extracted values reactive:

```svelte
<script>
	function getData() {
		return { a: 1, b: 2, c: 3 };
	}

	// All three are individual deriveds
	let { a, b, c } = $derived(getData());

	// Roughly equivalent to:
	let _data = $derived(getData());
	let a = $derived(_data.a);
	let b = $derived(_data.b);
	let c = $derived(_data.c);
</script>
```

## Update Propagation (Push-Pull)

Svelte uses **push-pull reactivity**:

1. **Push:** When state changes, dependents are notified immediately
2. **Pull:** Derived values only recalculate when **read**

### Skipping Downstream Updates

If a derived's new value is referentially identical to the old value, downstream updates are skipped:

```svelte
<script>
	let count = $state(0);
	let large = $derived(count > 10);
</script>

<button onclick={() => count++}>
	{large}
</button>
```

- When `count` goes 0→1→2...→10: `large` stays `false`, UI doesn't update
- When `count` goes 10→11: `large` becomes `true`, UI updates once
- When `count` goes 11→12→13: `large` stays `true`, UI doesn't update

**Result:** UI only updates when `large` actually changes, not every time `count` changes.

## Common Patterns

### Filtering and Mapping

```svelte
<script>
	let items = $state([1, 2, 3, 4, 5, 6]);
	let filterMin = $state(0);

	let filtered = $derived(items.filter(n => n > filterMin));
	let doubled = $derived(filtered.map(n => n * 2));
	let sum = $derived(doubled.reduce((a, b) => a + b, 0));
</script>
```

### Derived from Multiple Sources

```svelte
<script>
	let firstName = $state('Ada');
	let lastName = $state('Lovelace');
	let title = $state('Countess');

	let fullName = $derived(`${title} ${firstName} ${lastName}`);
	let initials = $derived(`${firstName[0]}${lastName[0]}`);
</script>
```

### Complex Business Logic

```svelte
<script>
	let cart = $state([
		{ id: 1, price: 10, quantity: 2 },
		{ id: 2, price: 20, quantity: 1 }
	]);

	let discountCode = $state('');

	let subtotal = $derived(
		cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
	);

	let discount = $derived.by(() => {
		if (discountCode === 'SAVE10') return subtotal * 0.1;
		if (discountCode === 'SAVE20') return subtotal * 0.2;
		return 0;
	});

	let total = $derived(subtotal - discount);
</script>

<p>Subtotal: ${subtotal}</p>
<p>Discount: ${discount}</p>
<p>Total: ${total}</p>
```

### Validation

```svelte
<script>
	let email = $state('');
	let password = $state('');

	let emailValid = $derived(email.includes('@') && email.includes('.'));
	let passwordValid = $derived(password.length >= 8);
	let formValid = $derived(emailValid && passwordValid);

	let emailError = $derived(!emailValid && email.length > 0 ? 'Invalid email' : '');
	let passwordError = $derived(!passwordValid && password.length > 0 ? 'Too short' : '');
</script>
```

## Performance Considerations

### Memoization

Derived values are **memoized** — they only recalculate when dependencies change:

```svelte
<script>
	let items = $state([1, 2, 3]);

	// Expensive calculation only runs when `items` changes
	let sorted = $derived(items.slice().sort((a, b) => b - a));
</script>
```

### Avoid Creating New Objects

If you return a new object/array every time, downstream components will always re-render:

```svelte
<script>
	let count = $state(0);

	// ❌ Creates new object every time
	let bad = $derived({ value: count });

	// ✅ Returns same object when count doesn't change
	let good = $derived(count);
</script>
```

### Lazy Evaluation

Deriveds only calculate when read:

```svelte
<script>
	let show = $state(false);
	let items = $state([1, 2, 3]);

	// Only calculates when `show` is true
	let expensive = $derived.by(() => {
		console.log('Calculating...');
		return items.reduce((sum, n) => sum + n ** 2, 0);
	});
</script>

{#if show}
	<p>{expensive}</p>
{/if}
```

## Common Pitfalls

### Using $effect Instead of $derived

❌ **Don't do this:**
```svelte
<script>
	let count = $state(0);
	let doubled = $state(0);

	$effect(() => {
		doubled = count * 2; // ❌ Wrong!
	});
</script>
```

✅ **Do this:**
```svelte
<script>
	let count = $state(0);
	let doubled = $derived(count * 2); // ✅ Correct!
</script>
```

### Side Effects in Deriveds

```svelte
<script>
	let count = $state(0);

	// ❌ Side effects not allowed
	let bad = $derived.by(() => {
		count++; // Error!
		console.log(count); // Discouraged
		return count * 2;
	});

	// ✅ Pure calculation
	let good = $derived(count * 2);
</script>
```

### Reading Without Tracking

```svelte
<script>
	let a = $state(1);
	let b = $state(2);

	// ❌ `b` is not tracked (not read)
	let result = $derived(a + 10);

	// Change to `b` won't cause recalculation
</script>
```

## Best Practices

1. **Keep deriveds pure** - No side effects
2. **Use `$derived`, not `$effect`** - For computed values
3. **Break complex calculations into steps**
   ```js
   let step1 = $derived(calculate1(data));
   let step2 = $derived(calculate2(step1));
   let final = $derived(calculate3(step2));
   ```
4. **Avoid expensive calculations in templates** - Use derived instead
5. **Consider referential equality** - Return same objects when possible
