# Architecture Patterns for Claude Agent SDK

This file contains detailed implementation patterns for different agent architectures.

## Pattern 1: CLI/Specialized Agent

**Best for:** Command-line tools, specialized workflows, batch processing

```typescript
// src/agent.ts
import { query, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';
import { myTools } from './tools/index.js';

const SYSTEM_PROMPT = `You are a specialized agent that...
[Detailed instructions about capabilities and tools]`;

export async function runAgent(userPrompt: string) {
  // Create MCP server at query time (not module level)
  const server = createSdkMcpServer({
    name: 'my-agent',
    version: '1.0.0',
    tools: myTools,
  });

  // Query with streaming
  const messages = query({
    prompt: userPrompt,
    options: {
      systemPrompt: SYSTEM_PROMPT,
      permissionMode: 'bypassPermissions',
      mcpServers: {
        'my-agent': server,
      },
    },
  });

  // Process stream
  for await (const event of messages) {
    if (event.type === 'assistant') {
      for (const content of event.message.content) {
        if (content.type === 'text') {
          process.stdout.write(content.text);
        }
      }
    }
  }
}
```

## Pattern 2: Web Server Agent with SSE

**Best for:** Web applications, API servers, real-time UIs

```typescript
// src/routes/agent.ts
import { query, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';

app.post('/agent/stream', async (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const server = createSdkMcpServer({
    name: 'web-agent',
    version: '1.0.0',
    tools: createContextualTools(req.session),
  });

  const messages = query({
    prompt: req.body.prompt,
    options: {
      systemPrompt: SYSTEM_PROMPT,
      mcpServers: { 'web-agent': server },
    },
  });

  for await (const event of messages) {
    res.write(`data: ${JSON.stringify(event)}\n\n`);
  }

  res.end();
});
```

## Pattern 3: Plugin/Framework Agent

**Best for:** Extensible systems, plugin architectures, reusable frameworks

```typescript
// src/engine.ts
export class AgentEngine {
  constructor(private plugin: Plugin) {}

  async stream(prompt: string): Promise<void> {
    const mcpServers: Record<string, any> = {};

    if (this.plugin.tools.length > 0) {
      const serverName = `${this.plugin.name}-tools`;
      mcpServers[serverName] = createSdkMcpServer({
        name: serverName,
        version: this.plugin.version ?? '1.0.0',
        tools: this.plugin.tools,
      });
    }

    const messages = query({
      prompt,
      options: {
        systemPrompt: this.plugin.systemPrompt,
        permissionMode: 'bypassPermissions',
        allowedTools: this.plugin.allowedTools,
        mcpServers,
      },
    });

    for await (const event of messages) {
      await this.plugin.handleEvent(event);
    }
  }
}
```

## Pattern 4: Monorepo Full-Stack Application

**Best for:** Full-stack apps with frontend + backend, complex web applications

Site Studio is an example of this pattern using npm workspaces.

**Project Structure:**
```
my-app/
├── package.json           # Root workspace config
├── packages/
│   ├── backend/
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── index.ts   # Express server
│   │   │   ├── agent.ts   # Agent logic
│   │   │   └── tools/     # Tool definitions
│   │   └── dist/          # Build output
│   └── frontend/
│       ├── package.json
│       ├── src/
│       └── dist/
```

**Root package.json:**
```json
{
  "name": "my-app",
  "private": true,
  "workspaces": ["packages/*"],
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\"",
    "dev:backend": "npm run dev --workspace=packages/backend",
    "dev:frontend": "npm run dev --workspace=packages/frontend",
    "build": "npm run build --workspace=packages/backend && npm run build --workspace=packages/frontend"
  },
  "devDependencies": {
    "concurrently": "^9.1.2"
  }
}
```

**Backend package.json:**
```json
{
  "name": "@my-app/backend",
  "type": "module",
  "scripts": {
    "dev": "tsc && node dist/index.js",
    "build": "tsc"
  },
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.1.14",
    "express": "^4.21.2",
    "zod": "^3.24.1"
  }
}
```

**Backend agent.ts:**
```typescript
import { query, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';
import { createFileTools } from './tools/file-tools.js';

export async function runAgent(
  prompt: string,
  projectPath: string,
  sessionId?: string
): Promise<AsyncIterable<any>> {
  const tools = createFileTools(projectPath);

  const server = createSdkMcpServer({
    name: 'my-app',
    version: '1.0.0',
    tools,
  });

  const queryOptions: any = {
    permissionMode: 'bypassPermissions',  // Required for standalone servers!
    systemPrompt: SYSTEM_PROMPT,
    mcpServers: { 'my-app': server },
  };

  if (sessionId) {
    queryOptions.resume = sessionId;
  }

  return query({ prompt, options: queryOptions });
}
```

**Backend index.ts (Express):**
```typescript
import express from 'express';
import { runAgent } from './agent.js';

const app = express();
app.use(express.json());

app.post('/api/query', async (req, res) => {
  const { prompt, projectId, sessionId } = req.body;
  const projectPath = path.join(PROJECTS_DIR, projectId);

  // Set up SSE
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  try {
    const stream = await runAgent(prompt, projectPath, sessionId);

    for await (const event of stream) {
      res.write(`data: ${JSON.stringify(event)}\n\n`);
    }

    res.write('data: [DONE]\n\n');
    res.end();
  } catch (error: any) {
    res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
    res.end();
  }
});

app.listen(3001, () => {
  console.log('Backend running on http://localhost:3001');
});
```

**Benefits of Monorepo Pattern:**
- Share TypeScript configurations
- Single `npm install` for all dependencies
- Coordinated development with `concurrently`
- Type safety across packages
- Unified build and deploy processes
