# Working Examples from Production Implementations

This document provides real-world examples from five successful Claude Agent TypeScript SDK implementations.

## Project Overview

### 1. availability-cascade-search
**Type**: CLI Agent for library availability research
**SDK Version**: 0.1.14
**Files**: `/home/zweb/apps/availability-cascade-search/`

#### Key Features
- Python subprocess integration for WorldCat and OpenAlex APIs
- Cascading search across library tiers
- CSV output generation
- 157-line system prompt with tier definitions

#### Tool Pattern: Subprocess Wrapper
```typescript
// From: src/tools/worldcat-tools.ts
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { spawn } from 'child_process';
import { z } from 'zod';

export const searchWorldcat = tool(
  'search_worldcat',
  'Search WorldCat for bibliographic records',
  z.object({
    query: z.string().describe('Search query'),
    limit: z.number().optional().describe('Max results (default: 10)'),
  }).shape,
  async ({ query, limit = 10 }) => {
    return new Promise((resolve, reject) => {
      const python = spawn('python3', [
        'scripts/worldcat_search.py',
        '--query', query,
        '--limit', String(limit),
      ]);

      let stdout = '';
      let stderr = '';

      python.stdout.on('data', (data) => stdout += data.toString());
      python.stderr.on('data', (data) => stderr += data.toString());

      python.on('close', (code) => {
        if (code !== 0) {
          resolve({
            content: [{
              type: 'text' as const,
              text: JSON.stringify({ error: stderr }),
            }],
          });
          return;
        }

        try {
          const result = JSON.parse(stdout);
          resolve({
            content: [{
              type: 'text' as const,
              text: JSON.stringify(result, null, 2),
            }],
          });
        } catch (e) {
          reject(new Error(`Parse error: ${stdout}`));
        }
      });
    });
  }
);
```

---

### 2. ill-worldcat-enrichment
**Type**: CLI Agent for metadata enrichment
**SDK Version**: 0.1.14
**Files**: `/home/zweb/apps/ill-worldcat-enrichment/`

#### Key Features
- CSV row-by-row processing with streaming
- Real-time output display
- WorldCat metadata enrichment
- 170+ line system prompt with search strategies

#### Tool Pattern: CSV Data Tools
```typescript
// From: src/tools/csv-tools.ts
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';
import { promises as fs } from 'fs';

export const readCsv = tool(
  'read_csv',
  'Read and parse CSV file',
  z.object({
    path: z.string().describe('Path to CSV file'),
  }).shape,
  async ({ path }) => {
    const content = await fs.readFile(path, 'utf-8');
    const records = parse(content, { columns: true });
    return {
      content: [{
        type: 'text' as const,
        text: JSON.stringify(records, null, 2),
      }],
    };
  }
);

export const writeCsv = tool(
  'write_csv',
  'Write data to CSV file',
  z.object({
    path: z.string().describe('Output file path'),
    data: z.array(z.record(z.any())).describe('Array of records'),
  }).shape,
  async ({ path, data }) => {
    const csv = stringify(data, { header: true });
    await fs.writeFile(path, csv, 'utf-8');
    return {
      content: [{
        type: 'text' as const,
        text: `Wrote ${data.length} records to ${path}`,
      }],
    };
  }
);

export const csvTools = [readCsv, writeCsv];
```

---

### 3. obsidian-agent-plugin
**Type**: Obsidian Plugin for vault organization
**SDK Version**: 0.1.14
**Files**: `/home/zweb/apps/obsidian-agent-plugin/`

#### Key Features
- Dynamic tool creation from JSON config
- Obsidian API integration
- Plugin settings UI
- esbuild compilation (not tsc)

#### Tool Pattern: Dynamic Tools from Config
```typescript
// From: src/main.ts (simplified)
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

interface ToolConfig {
  name: string;
  description: string;
  parameters: {
    name: string;
    type: 'string' | 'number' | 'boolean';
    description: string;
    optional?: boolean;
  }[];
  command: string;
}

function createDynamicTools(configs: ToolConfig[]) {
  return configs.map((config) => {
    // Build Zod schema from config
    const schemaShape: Record<string, z.ZodType> = {};

    for (const param of config.parameters) {
      let zodType: z.ZodType;

      switch (param.type) {
        case 'number':
          zodType = z.number();
          break;
        case 'boolean':
          zodType = z.boolean();
          break;
        default:
          zodType = z.string();
      }

      if (param.optional) {
        zodType = zodType.optional();
      }

      zodType = zodType.describe(param.description);
      schemaShape[param.name] = zodType;
    }

    return tool(
      config.name,
      config.description,
      z.object(schemaShape).shape,
      async (params) => {
        // Execute command with params
        const result = await executeToolCommand(config.command, params);
        return {
          content: [{
            type: 'text' as const,
            text: JSON.stringify(result),
          }],
        };
      }
    );
  });
}

// Load from plugin settings
const toolConfigs = this.settings.tools;
const dynamicTools = createDynamicTools(toolConfigs);
```

---

### 4. site-agent/core
**Type**: Framework/Library for reusable agents
**SDK Version**: 0.1.5 (older)
**Files**: `/home/zweb/apps/site-agent/packages/core/`

#### Key Features
- Plugin architecture with DomainPlugin interface
- Knowledge base loading from markdown files
- Conversation history management
- Dynamic MCP server creation

#### Pattern: Framework Engine
```typescript
// From: packages/core/src/agent/engine.ts
import { query, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';

export class AgentEngine {
  constructor(
    private plugin: DomainPlugin,
    private conversationHistory: Message[] = []
  ) {}

  async stream(userPrompt: string, abortController?: AbortController) {
    await this.initialize();

    // Build full prompt with history
    const fullPrompt = this.buildPromptWithHistory(userPrompt);

    // Create MCP servers dynamically
    const mcpServers: Record<string, any> = {};

    if (this.plugin.tools.length > 0) {
      const serverName = `${this.plugin.name}-tools`;
      mcpServers[serverName] = createSdkMcpServer({
        name: serverName,
        version: this.plugin.version ?? '1.0.0',
        tools: this.plugin.tools,
      });
    }

    // Query with dynamic configuration
    const responseStream = query({
      prompt: fullPrompt,
      options: {
        systemPrompt: this.systemPrompt ?? '',
        permissionMode: 'bypassPermissions',
        allowedTools: this.plugin.allowedTools ?? [
          ...this.plugin.tools.map((t) => t.name),
          'WebSearch',
          'WebFetch',
        ],
        mcpServers,
        ...(abortController ? { abortController } : {}),
      },
    });

    // Process stream
    for await (const event of responseStream) {
      if (event.type === 'assistant') {
        // Handle assistant message
        this.conversationHistory.push({
          role: 'assistant',
          content: event.message.content,
        });
      }
    }
  }

  private async initialize() {
    // Load knowledge base
    if (this.plugin.knowledgeBasePath) {
      const files = await this.loadMarkdownFiles(this.plugin.knowledgeBasePath);
      this.systemPrompt = this.plugin.systemPrompt + '\n\n' + files.join('\n');
    }
  }
}
```

---

### 5. site-studio/backend
**Type**: Express web server for site building
**SDK Version**: 0.1.14
**Files**: `/home/zweb/apps/site-studio/packages/backend/`

#### Key Features
- SSE streaming to web clients
- Factory-based tool creation with context
- Planning mode and execution mode
- Session management

#### Tool Pattern: Factory with Closure Context
```typescript
// From: packages/backend/src/tools/file-tools.ts
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';
import { promises as fs } from 'fs';
import { join } from 'path';

export function createFileTools(projectPath: string) {
  const listFiles = tool(
    'list_files',
    'List all files and directories in the project',
    z.object({
      directory: z.string().optional().describe('Subdirectory to list'),
    }).shape,
    async (params) => {
      const targetDir = params.directory
        ? join(projectPath, params.directory)
        : projectPath;

      const files = await fs.readdir(targetDir, { withFileTypes: true });
      const tree = files.map((f) => {
        const type = f.isDirectory() ? '[DIR]' : '[FILE]';
        return `${type} ${f.name}`;
      });

      return {
        content: [{
          type: 'text' as const,
          text: JSON.stringify({ success: true, tree: tree.join('\n') }),
        }],
      };
    }
  );

  const readFile = tool(
    'read_file',
    'Read a file from the project',
    z.object({
      path: z.string().describe('Relative path from project root'),
    }).shape,
    async ({ path }) => {
      try {
        const fullPath = join(projectPath, path);
        const content = await fs.readFile(fullPath, 'utf-8');
        return {
          content: [{
            type: 'text' as const,
            text: content,
          }],
        };
      } catch (error: any) {
        return {
          content: [{
            type: 'text' as const,
            text: `Error reading file: ${error.message}`,
          }],
        };
      }
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
      try {
        const fullPath = join(projectPath, path);
        await fs.writeFile(fullPath, content, 'utf-8');
        return {
          content: [{
            type: 'text' as const,
            text: `Successfully wrote to ${path}`,
          }],
        };
      } catch (error: any) {
        return {
          content: [{
            type: 'text' as const,
            text: `Error writing file: ${error.message}`,
          }],
        };
      }
    }
  );

  return [listFiles, readFile, writeFile];
}
```

#### Pattern: SSE Streaming Endpoint
```typescript
// From: packages/backend/src/index.ts
import express from 'express';
import { query, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';

const app = express();

app.post('/agent/stream', async (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const { prompt, projectPath, sessionId } = req.body;

  // Create tools with context
  const tools = createFileTools(projectPath);

  // Create MCP server
  const server = createSdkMcpServer({
    name: 'site-builder',
    version: '1.0.0',
    tools,
  });

  // Query
  const messages = query({
    prompt,
    options: {
      systemPrompt: SYSTEM_PROMPT,
      permissionMode: 'bypassPermissions',
      mcpServers: {
        'site-builder': server,
      },
    },
  });

  // Stream to client
  try {
    for await (const event of messages) {
      res.write(`data: ${JSON.stringify(event)}\n\n`);
    }
    res.write('data: [DONE]\n\n');
    res.end();
  } catch (error: any) {
    res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
    res.end();
  }
});
```

---

## Common Patterns Summary

### 1. Tool Organization Patterns

**Individual Exports + Array Export**
```typescript
export const tool1 = tool(...);
export const tool2 = tool(...);
export const allTools = [tool1, tool2];
```

**Factory Functions**
```typescript
export function createTools(context: Context) {
  return [tool1, tool2, tool3];
}
```

**Grouped by Domain**
```typescript
export const fileTools = [readFile, writeFile];
export const apiTools = [searchApi, fetchApi];
```

### 2. MCP Server Creation

**At Query Time (Preferred)**
```typescript
async function runAgent() {
  const server = createSdkMcpServer({ name, version, tools });
  const messages = query({ options: { mcpServers: { name: server } } });
}
```

**Dynamic Server Creation**
```typescript
const mcpServers: Record<string, any> = {};
if (tools.length > 0) {
  mcpServers[name] = createSdkMcpServer({ name, version, tools });
}
```

### 3. Stream Processing

**Simple Text Output**
```typescript
for await (const event of messages) {
  if (event.type === 'assistant') {
    for (const block of event.message.content) {
      if (block.type === 'text') {
        process.stdout.write(block.text);
      }
    }
  }
}
```

**Structured Event Handling**
```typescript
for await (const event of messages) {
  switch (event.type) {
    case 'assistant':
      handleAssistant(event.message);
      break;
    case 'user':
      handleUser(event.message);
      break;
  }
}
```

### 4. Error Handling

**Tool-Level**
```typescript
try {
  const result = await operation();
  return { content: [{ type: 'text', text: JSON.stringify(result) }] };
} catch (error: any) {
  return { content: [{ type: 'text', text: `Error: ${error.message}` }] };
}
```

**Stream-Level**
```typescript
try {
  for await (const event of messages) {
    // Process
  }
} catch (error: any) {
  console.error('Agent error:', error);
}
```

---

## System Prompt Examples

All successful implementations use 100-170+ line system prompts with:
- Role definition
- Tool descriptions
- Workflow instructions
- Output format requirements
- Error handling strategies

See individual project files for complete examples:
- `/home/zweb/apps/availability-cascade-search/src/prompts.ts`
- `/home/zweb/apps/ill-worldcat-enrichment/src/prompts.ts`
- `/home/zweb/apps/site-studio/packages/backend/src/agent.ts`
