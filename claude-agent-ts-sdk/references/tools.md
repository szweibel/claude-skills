# Tool Wrapping Pattern

**Philosophy:** Create portable, composable tools as modules. Only wrap in MCP servers when needed for query execution.

## Basic Tool Definition

```typescript
// src/tools/my-tool.ts
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

export const myTool = tool(
  'my_tool_name',
  'Clear description of what this tool does',
  z.object({
    param1: z.string().describe('What param1 is for'),
    param2: z.number().optional().describe('Optional parameter'),
  }).shape,
  async (params) => {
    // Implementation
    const result = await doSomething(params.param1, params.param2);

    return {
      content: [{
        type: 'text',
        text: JSON.stringify(result, null, 2),
      }],
    };
  }
);
```

## Tool Composition Pattern

```typescript
// src/tools/index.ts
import { fileTools } from './file-tools.js';
import { apiTools } from './api-tools.js';
import { searchTool } from './search-tool.js';

// Export individual tools for selective use
export { fileTools, apiTools, searchTool };

// Export combined array for convenience
export const allTools = [
  ...fileTools,
  ...apiTools,
  searchTool,
];
```

## Tool Factories (Context-Aware Tools)

Create tools that close over context for session-specific data:

```typescript
// src/tools/file-tools.ts
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

export function createFileTools(projectPath: string) {
  const readFile = tool(
    'read_file',
    'Read a file from the project',
    z.object({
      path: z.string().describe('Relative path from project root'),
    }).shape,
    async ({ path }) => {
      const fullPath = join(projectPath, path);
      const content = await fs.readFile(fullPath, 'utf-8');
      return {
        content: [{ type: 'text', text: content }],
      };
    }
  );

  const writeFile = tool(
    'write_file',
    'Write content to a file',
    z.object({
      path: z.string().describe('Relative path from project root'),
      content: z.string().describe('File content'),
    }).shape,
    async ({ path, content }) => {
      const fullPath = join(projectPath, path);
      await fs.writeFile(fullPath, content, 'utf-8');
      return {
        content: [{ type: 'text', text: `Wrote to ${path}` }],
      };
    }
  );

  return [readFile, writeFile];
}

// Usage in agent:
const tools = createFileTools('/path/to/project');
const server = createSdkMcpServer({ name: 'files', version: '1.0.0', tools });
```

## Subprocess Wrapper Tools

Wrap external programs for deterministic operations:

```typescript
// src/tools/python-tools.ts
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { spawn } from 'child_process';
import { z } from 'zod';

export const runPythonScript = tool(
  'run_python_analysis',
  'Run Python data analysis script',
  z.object({
    query: z.string().describe('Search query for analysis'),
    limit: z.number().optional().describe('Max results'),
  }).shape,
  async ({ query, limit = 10 }) => {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn('python3', [
        'scripts/analyze.py',
        '--query', query,
        '--limit', String(limit),
      ]);

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python script failed: ${stderr}`));
          return;
        }

        try {
          const result = JSON.parse(stdout);
          resolve({
            content: [{
              type: 'text',
              text: JSON.stringify(result, null, 2),
            }],
          });
        } catch (e) {
          reject(new Error(`Failed to parse output: ${stdout}`));
        }
      });
    });
  }
);
```

## Dynamic Tool Creation

Generate tools from configuration:

```typescript
// src/tools/dynamic-tools.ts
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

export function createDynamicTools(config: ToolConfig[]) {
  return config.map((toolConfig) => {
    // Build Zod schema from config
    const schemaShape: Record<string, z.ZodType> = {};
    for (const param of toolConfig.parameters) {
      let zodType: z.ZodType = z.string();

      if (param.type === 'number') zodType = z.number();
      if (param.type === 'boolean') zodType = z.boolean();
      if (param.optional) zodType = zodType.optional();

      zodType = zodType.describe(param.description);
      schemaShape[param.name] = zodType;
    }

    return tool(
      toolConfig.name,
      toolConfig.description,
      z.object(schemaShape).shape,
      async (params) => {
        // Execute configured command
        const result = await executeCommand(toolConfig.command, params);
        return {
          content: [{ type: 'text', text: JSON.stringify(result) }],
        };
      }
    );
  });
}
```

## Error Handling in Tools

```typescript
export const myTool = tool(
  'my_tool',
  'Description',
  schema,
  async (params) => {
    try {
      const result = await riskyOperation(params);
      return {
        content: [{ type: 'text', text: JSON.stringify(result) }],
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            error: true,
            message: error.message,
            suggestion: 'Try adjusting parameters or check prerequisites',
          }),
        }],
        isError: true,
      };
    }
  }
);
```

## Common Tool Patterns

### CSV Processing Agent

```typescript
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';

export const readCsv = tool(
  'read_csv',
  'Read and parse CSV file',
  z.object({
    path: z.string(),
  }).shape,
  async ({ path }) => {
    const content = await fs.readFile(path, 'utf-8');
    const records = parse(content, { columns: true });
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(records, null, 2),
      }],
    };
  }
);

export const writeCsv = tool(
  'write_csv',
  'Write data to CSV file',
  z.object({
    path: z.string(),
    data: z.array(z.record(z.any())),
  }).shape,
  async ({ path, data }) => {
    const csv = stringify(data, { header: true });
    await fs.writeFile(path, csv, 'utf-8');
    return {
      content: [{
        type: 'text',
        text: `Wrote ${data.length} records to ${path}`,
      }],
    };
  }
);
```

### API Integration Tools

```typescript
export const searchApi = tool(
  'search_api',
  'Search external API',
  z.object({
    query: z.string(),
    filters: z.record(z.string()).optional(),
  }).shape,
  async ({ query, filters }) => {
    const params = new URLSearchParams({ q: query, ...filters });
    const response = await fetch(`https://api.example.com/search?${params}`);

    if (!response.ok) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ error: `API error: ${response.statusText}` }),
        }],
        isError: true,
      };
    }

    const data = await response.json();
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(data, null, 2),
      }],
    };
  }
);
```

## Best Practices

### DO

✅ **Export tools as both individual exports and arrays**
```typescript
export const tool1 = tool(...);
export const tool2 = tool(...);
export const myTools = [tool1, tool2];
```

✅ **Use Zod schemas with detailed descriptions**
```typescript
z.object({
  query: z.string().describe('The search query to execute'),
  limit: z.number().optional().describe('Maximum number of results (default: 10)'),
})
```

✅ **Use closures for context-aware tools**
```typescript
export function createTools(context: Context) {
  return [
    tool('name', 'desc', schema, async (params) => {
      // Has access to context via closure
      return processWithContext(context, params);
    })
  ];
}
```

### DON'T

❌ **Don't create full MCP servers for simple tools**
```typescript
// AVOID: Creating MCP server infrastructure
const server = new MCPServer(...);
server.registerTool(...);
// Use tool() wrapper instead
```

❌ **Don't use global state in tools**
```typescript
// BAD
let globalContext;
export const tool = tool('name', 'desc', schema, async () => {
  return useGlobalContext(globalContext); // Brittle!
});
```

❌ **Don't skip Zod validation**
```typescript
// BAD: No schema validation
tool('name', 'desc', {}, async (params: any) => { ... });
```
