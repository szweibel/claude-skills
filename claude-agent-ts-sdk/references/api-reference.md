# Claude Agent SDK API Reference

Quick reference for `@anthropic-ai/claude-agent-sdk` v0.1.14+

## Core Functions

### `query()`

Main entry point for agent interactions. Returns an async iterable of events.

```typescript
import { query } from '@anthropic-ai/claude-agent-sdk';

const messages = query({
  prompt: string,
  options?: QueryOptions
});

for await (const event of messages) {
  // Process events
}
```

#### Parameters

**prompt** (string, required)
- The user's input prompt
- Can be a simple string or complex multi-line text
- Example: `"Search for books about TypeScript"`

**options** (QueryOptions, optional)
- Configuration object for the query

#### QueryOptions

```typescript
interface QueryOptions {
  systemPrompt?: string;
  permissionMode?: 'bypassPermissions' | 'requestPermissions';
  mcpServers?: Record<string, MCPServer>;
  allowedTools?: string[];
  abortController?: AbortController;
  onToolCall?: (toolName: string, params: any) => void;
  onToolResult?: (toolName: string, result: any) => void;
}
```

**systemPrompt** (string)
- System-level instructions for the agent
- Defines role, capabilities, and behavior
- Typically 100-500 lines for production agents

**permissionMode** (string)
- `'bypassPermissions'`: Agent can use tools autonomously (recommended for most cases)
- `'requestPermissions'`: Agent asks for permission before tool use (interactive mode)

**mcpServers** (Record<string, MCPServer>)
- Map of server names to MCP server instances
- Keys are server identifiers, values are servers created with `createSdkMcpServer()`
- Example: `{ 'my-tools': server }`

**allowedTools** (string[])
- Whitelist of tool names the agent can use
- If omitted, all registered tools are allowed
- Example: `['search_database', 'WebSearch', 'WebFetch']`

**abortController** (AbortController)
- Standard Web API AbortController for canceling streams
- Useful for user-initiated cancellations

**onToolCall** (callback)
- Debug callback fired when agent calls a tool
- Receives: `(toolName: string, params: any) => void`

**onToolResult** (callback)
- Debug callback fired when tool returns
- Receives: `(toolName: string, result: any) => void`

#### Return Value

Returns `AsyncIterable<SDKMessage>` - stream of events

Event types:
- `{ type: 'assistant', message: Message }`
- `{ type: 'user', message: Message }`
- `{ type: 'error', error: Error }`

---

### `createSdkMcpServer()`

Creates an MCP server instance that wraps tools for use with `query()`.

```typescript
import { createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';

const server = createSdkMcpServer({
  name: string,
  version: string,
  tools: Tool[]
});
```

#### Parameters

**name** (string, required)
- Identifier for the server
- Used in logs and debugging
- Example: `'my-agent-tools'`

**version** (string, required)
- Semantic version string
- Example: `'1.0.0'`

**tools** (Tool[], required)
- Array of tools created with `tool()` function
- Can be empty array if no tools needed

#### Return Value

Returns `MCPServer` instance that can be passed to `query()` options.

---

### `tool()`

Creates a tool definition that the agent can call.

```typescript
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

const myTool = tool(
  name: string,
  description: string,
  schema: Record<string, z.ZodType>,
  handler: (params: any) => Promise<ToolResult>
);
```

#### Parameters

**name** (string, required)
- Tool identifier (snake_case recommended)
- Must be unique within server
- Example: `'search_database'`

**description** (string, required)
- Clear explanation of what the tool does
- Used by agent to decide when to call tool
- Should be specific and actionable
- Example: `'Search the product database for items matching a query'`

**schema** (Record<string, z.ZodType>, required)
- Zod schema object describing parameters
- **Must use `.shape` property**: `z.object({ ... }).shape`
- All parameters should have descriptions
- Example:
  ```typescript
  z.object({
    query: z.string().describe('Search query'),
    limit: z.number().optional().describe('Max results'),
  }).shape
  ```

**handler** (async function, required)
- Async function that implements tool logic
- Receives validated parameters
- Must return `ToolResult` object

#### Handler Parameters

Receives object with validated parameters matching the schema.

```typescript
async (params: { query: string; limit?: number }) => {
  // params are already validated against schema
}
```

#### Return Value: ToolResult

```typescript
interface ToolResult {
  content: ContentBlock[];
  isError?: boolean;
}

interface ContentBlock {
  type: 'text';
  text: string;
}
```

**content** (ContentBlock[], required)
- Array of content blocks to return to agent
- Currently only `type: 'text'` is supported
- Text should be JSON stringified for structured data

**isError** (boolean, optional)
- Set to `true` if tool execution failed
- Helps agent understand and report errors

#### Example

```typescript
const searchTool = tool(
  'search_products',
  'Search the product catalog for items',
  z.object({
    query: z.string().describe('Search query'),
    category: z.string().optional().describe('Filter by category'),
    limit: z.number().default(10).describe('Maximum results'),
  }).shape,
  async ({ query, category, limit }) => {
    try {
      const results = await database.search(query, category, limit);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(results, null, 2),
        }],
      };
    } catch (error: any) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ error: error.message }),
        }],
        isError: true,
      };
    }
  }
);
```

---

## Event Types

### SDKMessage

Union type of possible events in the stream:

```typescript
type SDKMessage =
  | { type: 'assistant'; message: Message }
  | { type: 'user'; message: Message }
  | { type: 'error'; error: Error };
```

### Message

```typescript
interface Message {
  role: 'assistant' | 'user';
  content: ContentBlock[];
}
```

### ContentBlock

```typescript
type ContentBlock =
  | { type: 'text'; text: string }
  | { type: 'tool_use'; id: string; name: string; input: any }
  | { type: 'tool_result'; tool_use_id: string; content: string };
```

---

## Common Patterns

### Basic Query

```typescript
const messages = query({
  prompt: 'Hello, how are you?',
  options: {
    systemPrompt: 'You are a helpful assistant.',
  },
});

for await (const event of messages) {
  if (event.type === 'assistant') {
    console.log(event.message.content);
  }
}
```

### Query with Tools

```typescript
const tools = [searchTool, fetchTool];

const server = createSdkMcpServer({
  name: 'my-tools',
  version: '1.0.0',
  tools,
});

const messages = query({
  prompt: 'Search for TypeScript books',
  options: {
    systemPrompt: 'You are a librarian assistant.',
    permissionMode: 'bypassPermissions',
    mcpServers: {
      'my-tools': server,
    },
  },
});

for await (const event of messages) {
  if (event.type === 'assistant') {
    console.log(event.message.content);
  }
}
```

### Query with Abort

```typescript
const abortController = new AbortController();

// Cancel after 30 seconds
setTimeout(() => abortController.abort(), 30000);

const messages = query({
  prompt: 'Long running task',
  options: {
    abortController,
  },
});

try {
  for await (const event of messages) {
    // Process
  }
} catch (error: any) {
  if (error.name === 'AbortError') {
    console.log('Query was aborted');
  }
}
```

### Query with Debug Logging

```typescript
const messages = query({
  prompt: 'Test query',
  options: {
    onToolCall: (name, params) => {
      console.log(`[CALL] ${name}`, params);
    },
    onToolResult: (name, result) => {
      console.log(`[RESULT] ${name}`, result);
    },
  },
});
```

---

## Tool Patterns

### Simple Data Tool

```typescript
const getTool = tool(
  'get_data',
  'Retrieve data by ID',
  z.object({
    id: z.string().describe('Data ID'),
  }).shape,
  async ({ id }) => {
    const data = await database.get(id);
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(data),
      }],
    };
  }
);
```

### Tool with Validation

```typescript
const createTool = tool(
  'create_record',
  'Create a new record',
  z.object({
    name: z.string().min(1).max(100),
    email: z.string().email(),
    age: z.number().min(0).max(150),
  }).shape,
  async (params) => {
    // Params are already validated
    const record = await database.create(params);
    return {
      content: [{
        type: 'text',
        text: `Created record ${record.id}`,
      }],
    };
  }
);
```

### Tool with Error Handling

```typescript
const apiTool = tool(
  'call_api',
  'Call external API',
  z.object({
    endpoint: z.string(),
  }).shape,
  async ({ endpoint }) => {
    try {
      const response = await fetch(endpoint);

      if (!response.ok) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              error: `API error: ${response.statusText}`,
            }),
          }],
          isError: true,
        };
      }

      const data = await response.json();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(data),
        }],
      };
    } catch (error: any) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            error: error.message,
          }),
        }],
        isError: true,
      };
    }
  }
);
```

### Context-Aware Tool (Factory)

```typescript
function createContextTool(context: Context) {
  return tool(
    'process_with_context',
    'Process data using context',
    z.object({
      data: z.string(),
    }).shape,
    async ({ data }) => {
      // Closure has access to context
      const result = context.process(data);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result),
        }],
      };
    }
  );
}

// Usage
const context = { process: (d) => d.toUpperCase() };
const tool = createContextTool(context);
```

---

## Type Definitions

### Complete TypeScript Types

```typescript
import { z } from 'zod';

// Tool definition
type Tool = {
  name: string;
  description: string;
  inputSchema: Record<string, z.ZodType>;
  execute: (params: any) => Promise<ToolResult>;
};

// Tool result
type ToolResult = {
  content: ContentBlock[];
  isError?: boolean;
};

// Content block
type ContentBlock = {
  type: 'text';
  text: string;
};

// MCP Server
type MCPServer = {
  name: string;
  version: string;
  tools: Tool[];
};

// Query options
type QueryOptions = {
  systemPrompt?: string;
  permissionMode?: 'bypassPermissions' | 'requestPermissions';
  mcpServers?: Record<string, MCPServer>;
  allowedTools?: string[];
  abortController?: AbortController;
  onToolCall?: (toolName: string, params: any) => void;
  onToolResult?: (toolName: string, result: any) => void;
};

// SDK message (event)
type SDKMessage =
  | { type: 'assistant'; message: Message }
  | { type: 'user'; message: Message }
  | { type: 'error'; error: Error };

// Message
type Message = {
  role: 'assistant' | 'user';
  content: ContentBlock[];
};
```

---

## Best Practices

### 1. Tool Naming

- Use snake_case: `search_database`, not `searchDatabase`
- Be specific: `get_user_by_id`, not `get`
- Use verbs: `create_record`, `delete_file`, `search_products`

### 2. Tool Descriptions

- Explain what the tool does
- Mention when to use it
- Include parameter context
- Be specific and actionable

```typescript
// Good
'Search the product database for items matching a query string. Use this when the user asks about products, inventory, or items for sale.'

// Bad
'Search'
```

### 3. Schema Descriptions

- Describe every parameter
- Include constraints and defaults
- Provide examples if helpful

```typescript
z.object({
  query: z.string()
    .describe('Search query (e.g., "laptop", "book about python")'),
  limit: z.number()
    .min(1)
    .max(100)
    .default(10)
    .describe('Maximum number of results to return (1-100, default: 10)'),
})
```

### 4. Error Handling

- Always use try-catch in tool handlers
- Return errors in tool results, don't throw
- Set `isError: true` for errors
- Provide helpful error messages

### 5. Tool Returns

- Always return JSON-stringified data for structured results
- Use consistent format across tools
- Include success/error indicators
- Provide actionable information

```typescript
// Good
return {
  content: [{
    type: 'text',
    text: JSON.stringify({
      success: true,
      data: results,
      count: results.length,
    }),
  }],
};

// Also good
return {
  content: [{
    type: 'text',
    text: JSON.stringify({
      error: true,
      message: 'Database connection failed',
      suggestion: 'Check database credentials',
    }),
  }],
  isError: true,
};
```

---

## Limitations

### Current SDK Limitations (v0.1.14)

1. **Content Types**: Only `type: 'text'` is supported in tool returns
2. **Streaming**: Cannot stream partial tool results
3. **Multi-modal**: No image or file support in tool I/O
4. **Conversation History**: Must be managed manually
5. **Caching**: System prompt caching not exposed in API

### Workarounds

**For large data returns:**
```typescript
// Return summary + reference
return {
  content: [{
    type: 'text',
    text: JSON.stringify({
      summary: 'Found 1000 results',
      preview: results.slice(0, 10),
      note: 'Full results saved to results.json',
    }),
  }],
};
```

**For file operations:**
```typescript
// Return file path, not contents
return {
  content: [{
    type: 'text',
    text: `File saved to: ${filepath}\nSize: ${size} bytes`,
  }],
};
```

---

## Version Compatibility

This reference covers SDK version 0.1.14. For other versions:

- **0.1.5**: Older version, missing some features
- **0.1.14+**: Current recommended version
- **Latest**: Check npm for updates

Check installed version:
```bash
npm list @anthropic-ai/claude-agent-sdk
```

Update to latest:
```bash
npm install @anthropic-ai/claude-agent-sdk@latest
```
