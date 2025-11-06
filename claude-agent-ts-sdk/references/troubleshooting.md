# Troubleshooting Guide

Common issues and solutions for Claude Agent TypeScript SDK implementations.

## Installation Issues

### Issue: Module not found errors after installation

**Symptoms:**
```
Error: Cannot find module '@anthropic-ai/claude-agent-sdk'
```

**Solutions:**

1. **Verify package.json has ES modules enabled**
```json
{
  "type": "module"
}
```

2. **Check import syntax**
```typescript
// Correct
import { query, tool } from '@anthropic-ai/claude-agent-sdk';

// Incorrect (CommonJS)
const { query } = require('@anthropic-ai/claude-agent-sdk');
```

3. **Reinstall dependencies**
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: TypeScript compilation errors with SDK types

**Symptoms:**
```
error TS2307: Cannot find module '@anthropic-ai/claude-agent-sdk' or its corresponding type declarations
```

**Solutions:**

1. **Update tsconfig.json**
```json
{
  "compilerOptions": {
    "module": "Node16",
    "moduleResolution": "Node16",
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

2. **Install @types/node**
```bash
npm install --save-dev @types/node
```

---

## Runtime Errors


### Issue: Stream never completes or hangs

**Symptoms:**
- Agent stream starts but never finishes
- No error messages
- Process doesn't exit

**Solutions:**

1. **Always use for-await, never Promise.all**
```typescript
// Correct
for await (const event of messages) {
  // Process
}

// Incorrect
await Promise.all(messages); // Won't work with async iterables
```

2. **Check for proper error handling**
```typescript
try {
  for await (const event of messages) {
    // Process
  }
} catch (error) {
  console.error('Stream error:', error);
  process.exit(1);
}
```

3. **Add timeout for debugging**
```typescript
const timeout = setTimeout(() => {
  console.error('Stream timeout after 60s');
  process.exit(1);
}, 60000);

try {
  for await (const event of messages) {
    // Process
  }
} finally {
  clearTimeout(timeout);
}
```

### Issue: "Claude Code process exited with code 1"

**Symptoms:**
```
{"error":"Claude Code process exited with code 1"}
```
- Standalone server crashes immediately when query() is called
- Error appears in SSE stream
- Agent never responds

**Root Cause:**
Using `'interactive'` permission mode in a standalone application. The SDK tries to launch Claude Code to show permission prompts, but Claude Code isn't running.

**Solutions:**

1. **Always use 'bypassPermissions' for standalone servers**
```typescript
// ✅ CORRECT for Express servers, CLI tools, etc.
const messages = query({
  prompt,
  options: {
    permissionMode: 'bypassPermissions',  // Required!
    systemPrompt,
    mcpServers,
  },
});
```

2. **Remove conditional permission modes**
```typescript
// ❌ WRONG - causes crash in 'plan' mode
permissionMode: mode === 'execute' ? 'bypassPermissions' : 'interactive',

// ✅ CORRECT - always bypass for standalone
permissionMode: 'bypassPermissions',
```

3. **Don't set pathToClaudeCodeExecutable**
```typescript
// ❌ WRONG - this won't fix the issue
pathToClaudeCodeExecutable: '/path/to/claude',

// The issue is the permission mode, not the path
```

**When to use each permission mode:**
- `'bypassPermissions'` - Standalone servers, CLIs, background agents (most cases)
- `'interactive'` - ONLY when running inside Claude Code with UI
- `'allowedTools'` - When restricting tool access programmatically

### Issue: Tools not being called by agent

**Symptoms:**
- Agent responds but never uses tools
- No tool_use events in stream
- Agent says "I don't have access to that capability"

**Solutions:**

1. **Verify tool registration in MCP server**
```typescript
const server = createSdkMcpServer({
  name: 'my-server',
  version: '1.0.0',
  tools: [tool1, tool2], // Make sure tools array is populated
});

console.log('Registered tools:', server.tools.length); // Debug
```

2. **Check tool descriptions are clear**
```typescript
// Good: Specific, actionable description
tool(
  'search_database',
  'Search the product database for items matching a query string',
  // ...
)

// Bad: Vague description
tool(
  'search',
  'Search',
  // ...
)
```

3. **Verify MCP server is passed to query**
```typescript
const messages = query({
  prompt,
  options: {
    mcpServers: {
      'my-server': server, // Must match a server name
    },
  },
});
```

4. **Check system prompt mentions tools**
```typescript
const systemPrompt = `You have access to the following tools:

- search_database: Search for products
- get_details: Get product details

Always use these tools when the user asks about products.`;
```

### Issue: Tool execution errors not surfaced

**Symptoms:**
- Tool fails but agent continues without error
- Silent failures
- Agent makes assumptions instead of reporting errors

**Solutions:**

1. **Return errors in tool responses**
```typescript
tool('my_tool', 'desc', schema, async (params) => {
  try {
    const result = await operation(params);
    return {
      content: [{ type: 'text', text: JSON.stringify(result) }],
    };
  } catch (error: any) {
    // Return error in content, don't throw
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          error: true,
          message: error.message,
          stack: error.stack,
        }),
      }],
      isError: true,
    };
  }
});
```

2. **Add logging to tools**
```typescript
tool('my_tool', 'desc', schema, async (params) => {
  console.log('[TOOL CALL]', 'my_tool', params);

  try {
    const result = await operation(params);
    console.log('[TOOL SUCCESS]', 'my_tool', result);
    return { content: [{ type: 'text', text: JSON.stringify(result) }] };
  } catch (error: any) {
    console.error('[TOOL ERROR]', 'my_tool', error);
    return {
      content: [{ type: 'text', text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});
```

3. **Instruct agent to report errors in system prompt**
```typescript
const systemPrompt = `...

If a tool returns an error, you MUST:
1. Report the error to the user
2. Explain what went wrong
3. Suggest alternatives or next steps

Never ignore tool errors or make assumptions.`;
```

---

## Zod Schema Issues

### Issue: Validation errors with tool parameters

**Symptoms:**
```
ZodError: Expected string, received undefined
Invalid parameter type
```

**Solutions:**

1. **Make optional parameters truly optional**
```typescript
z.object({
  required: z.string().describe('Required param'),
  optional: z.string().optional().describe('Optional param'),
  withDefault: z.number().default(10).describe('Has default'),
})
```

2. **Provide clear descriptions**
```typescript
z.object({
  query: z.string().describe('The search query to execute'),
  limit: z.number()
    .min(1)
    .max(100)
    .default(10)
    .describe('Maximum number of results (1-100, default: 10)'),
})
```

3. **Use .shape for tool() function**
```typescript
// Correct
tool(
  'name',
  'desc',
  z.object({ param: z.string() }).shape,  // .shape!
  async (params) => { ... }
)

// Incorrect
tool(
  'name',
  'desc',
  z.object({ param: z.string() }),  // Missing .shape
  async (params) => { ... }
)
```

### Issue: Complex types not validated properly

**Symptoms:**
- Nested objects fail validation
- Arrays of objects not working
- Union types cause errors

**Solutions:**

1. **Use nested Zod schemas**
```typescript
const addressSchema = z.object({
  street: z.string(),
  city: z.string(),
  zip: z.string(),
});

const userSchema = z.object({
  name: z.string(),
  address: addressSchema,
  tags: z.array(z.string()),
});

tool('create_user', 'desc', userSchema.shape, async (params) => {
  // params is fully typed and validated
});
```

2. **Use z.union for alternatives**
```typescript
z.object({
  identifier: z.union([
    z.string().email(),
    z.string().uuid(),
  ]).describe('Email or UUID'),
})
```

---

## TypeScript Configuration Issues

### Issue: Import paths not resolving

**Symptoms:**
```
Cannot find module './tools/index.js'
Module not found: Error: Can't resolve './tools'
```

**Solutions:**

1. **Always use .js extension in imports (even for .ts files)**
```typescript
// Correct with ES modules
import { tools } from './tools/index.js';

// Incorrect
import { tools } from './tools/index';
import { tools } from './tools';
```

2. **Update tsconfig.json**
```json
{
  "compilerOptions": {
    "module": "Node16",
    "moduleResolution": "Node16",
    "esModuleInterop": true
  }
}
```

### Issue: Build output doesn't work

**Symptoms:**
```
node dist/index.js
Error [ERR_MODULE_NOT_FOUND]: Cannot find module
```

**Solutions:**

1. **Check package.json type**
```json
{
  "type": "module",
  "main": "./dist/index.js"
}
```

2. **Verify outDir in tsconfig.json**
```json
{
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  }
}
```

3. **Run build before starting**
```json
{
  "scripts": {
    "build": "tsc",
    "start": "npm run build && node dist/index.js",
    "dev": "tsx watch src/index.ts"
  }
}
```

---

## Streaming Issues

### Issue: Events out of order or duplicated

**Symptoms:**
- Tool results appear before tool calls
- Multiple identical events
- Conversation flow is confusing

**Solutions:**

1. **Process events in order**
```typescript
const events: any[] = [];

for await (const event of messages) {
  events.push(event); // Store in order

  // Process immediately for display
  if (event.type === 'assistant') {
    console.log(event.message.content);
  }
}

// events array now has complete, ordered conversation
```

2. **Don't buffer all events before processing**
```typescript
// Incorrect - loses streaming benefit
const events = [];
for await (const event of messages) {
  events.push(event);
}
// Process events array

// Correct - process as they arrive
for await (const event of messages) {
  processImmediately(event);
}
```

### Issue: SSE streaming disconnects or fails

**Symptoms:**
- Browser shows "EventSource failed"
- Connection drops mid-stream
- Client never receives DONE message

**Solutions:**

1. **Set proper headers**
```typescript
res.setHeader('Content-Type', 'text/event-stream');
res.setHeader('Cache-Control', 'no-cache');
res.setHeader('Connection', 'keep-alive');
res.setHeader('X-Accel-Buffering', 'no'); // Disable nginx buffering
```

2. **Send proper SSE format**
```typescript
for await (const event of messages) {
  // Must have "data: " prefix and "\n\n" suffix
  res.write(`data: ${JSON.stringify(event)}\n\n`);
}

// Send completion marker
res.write('data: [DONE]\n\n');
res.end();
```

3. **Handle client disconnect**
```typescript
req.on('close', () => {
  console.log('Client disconnected');
  abortController.abort();
});
```

---

## Performance Issues

### Issue: Agent responses are slow

**Solutions:**

1. **Use claude-3-5-sonnet-20241022 (latest model)**
```typescript
// Model is configured at SDK level, not in code
// Check ANTHROPIC_MODEL env var or SDK defaults
```

2. **Reduce system prompt size if > 10,000 tokens**
```typescript
// Too large
const systemPrompt = `...${knowledgeBase}...`; // 50k tokens

// Better
const systemPrompt = `...${relevantKnowledgeOnly}...`; // 5k tokens
```

3. **Stream responses to user immediately**
```typescript
for await (const event of messages) {
  if (event.type === 'assistant') {
    // Don't wait for full response
    displayPartialResponse(event.message.content);
  }
}
```

### Issue: High token usage costs

**Solutions:**

1. **Monitor conversation history size**
```typescript
const history: Message[] = [];

function addToHistory(message: Message) {
  history.push(message);

  // Limit history to last 10 messages
  if (history.length > 10) {
    history.shift();
  }
}
```

2. **Optimize system prompt**
- Remove redundant information
- Use concise language
- Reference external docs instead of including full text

3. **Use caching for system prompts**
```typescript
// System prompts > 1024 tokens can be cached
// Check SDK documentation for caching options
```

---

## Debugging Strategies

### Enable Verbose Logging

```typescript
const messages = query({
  prompt,
  options: {
    systemPrompt,
    mcpServers,
    // Add debug callbacks
    onToolCall: (name, params) => {
      console.log(`[TOOL CALL] ${name}`, JSON.stringify(params, null, 2));
    },
    onToolResult: (name, result) => {
      console.log(`[TOOL RESULT] ${name}`, JSON.stringify(result, null, 2));
    },
  },
});
```

### Log All Events

```typescript
for await (const event of messages) {
  console.log(`[EVENT] ${event.type}`, JSON.stringify(event, null, 2));

  // Process normally
  // ...
}
```

### Test Tools Independently

```typescript
// Create a test file: tests/tool-test.ts
async function testTool() {
  const result = await myTool.execute({ param: 'test value' });
  console.log('Tool result:', result);
}

testTool();
```

### Validate Setup

```typescript
// Validation helper
function validateSetup() {
  console.log('Checking setup...');

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('❌ ANTHROPIC_API_KEY not set');
    return false;
  }
  console.log('✅ API key configured');

  if (tools.length === 0) {
    console.warn('⚠️  No tools registered');
  } else {
    console.log(`✅ ${tools.length} tools registered`);
    tools.forEach((t) => console.log(`   - ${t.name}`));
  }

  console.log('✅ Setup validated');
  return true;
}

if (!validateSetup()) {
  process.exit(1);
}
```

---

## Common Anti-Patterns

### ❌ Creating MCP servers at module level

```typescript
// BAD: Server created at module load time
const server = createSdkMcpServer({ tools });

export function runAgent() {
  const messages = query({ options: { mcpServers: { 'name': server } } });
}
```

**Fix:** Create server in function scope
```typescript
// GOOD: Server created when needed
export function runAgent() {
  const server = createSdkMcpServer({ tools });
  const messages = query({ options: { mcpServers: { 'name': server } } });
}
```

### ❌ Using global state in tools

```typescript
// BAD: Global state
let context = '';

export const myTool = tool('name', 'desc', schema, async (params) => {
  return useContext(context); // Brittle, hard to test
});
```

**Fix:** Use closures or pass context
```typescript
// GOOD: Closure captures context
export function createTool(context: string) {
  return tool('name', 'desc', schema, async (params) => {
    return useContext(context);
  });
}
```

### ❌ Not handling async properly

```typescript
// BAD: Missing await
tool('name', 'desc', schema, (params) => {  // Not async!
  const result = fetchData(params);  // Promise, not data
  return { content: [{ type: 'text', text: result }] };  // Wrong!
});
```

**Fix:** Always use async/await
```typescript
// GOOD: Proper async
tool('name', 'desc', schema, async (params) => {
  const result = await fetchData(params);
  return { content: [{ type: 'text', text: JSON.stringify(result) }] };
});
```

---

## Getting Help

If you're still stuck after trying these solutions:

1. **Check the working examples**
   - See `working-examples.md` for production patterns
   - Compare your code to successful implementations

2. **Simplify to minimal reproduction**
   - Remove all non-essential code
   - Test with a single simple tool
   - Verify basic setup works before adding complexity

3. **Review the checklist**
   - ES modules enabled (`"type": "module"`)
   - Correct imports with .js extensions
   - Zod schemas use .shape
   - Tools return proper format
   - MCP server created and passed to query
   - for-await loop for streaming
   - Error handling in place

4. **Check SDK version**
   ```bash
   npm list @anthropic-ai/claude-agent-sdk
   # Should be >= 0.1.14
   ```

5. **Review TypeScript compilation**
   ```bash
   npx tsc --noEmit
   # Should complete with no errors
   ```
