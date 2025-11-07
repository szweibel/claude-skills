# Project Setup Guide

## 1. Package Configuration

```json
// package.json
{
  "name": "my-agent",
  "version": "1.0.0",
  "type": "module",
  "engines": {
    "node": ">=18.0.0"
  },
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@anthropic-ai/claude-agent-sdk": "^0.1.14",
    "zod": "^3.23.8"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "tsx": "^4.7.0",
    "typescript": "^5.3.3"
  }
}
```

**Key Points:**
- `"type": "module"` - Required for ES modules
- SDK version `^0.1.14` or later
- `zod` for schema validation
- `tsx` for development with watch mode

## 2. TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Key Settings:**
- `module: "Node16"` - For Node.js ES modules
- `strict: true` - Enable all strict type checking
- `declaration: true` - Generate `.d.ts` files for TypeScript consumers

## 3. Environment Setup

```bash
# .env.example (optional - for your own environment variables)
NODE_ENV=development
```

```gitignore
# .gitignore
node_modules/
dist/
.env
*.log
.DS_Store
```

**Note:** The SDK automatically uses Claude Code's authentication - no API keys needed in `.env`.

## 4. Directory Structure

### CLI/Simple Agent

```
my-agent/
├── src/
│   ├── index.ts              # Entry point
│   ├── agent.ts              # Agent implementation
│   ├── tools/
│   │   ├── index.ts          # Tool exports
│   │   ├── file-tools.ts     # File operations
│   │   └── api-tools.ts      # API calls
│   ├── prompts/
│   │   └── system.ts         # System prompts
│   └── types/
│       └── index.ts          # Type definitions
├── scripts/                   # Python/shell scripts called by tools
├── package.json
├── tsconfig.json
├── .env
└── .env.example
```

### Web Server Agent

```
my-agent/
├── src/
│   ├── index.ts              # Express server setup
│   ├── routes/
│   │   ├── agent.ts          # Agent endpoints
│   │   └── health.ts         # Health check
│   ├── agent/
│   │   ├── index.ts          # Agent logic
│   │   ├── tools/            # Tool definitions
│   │   └── prompts/          # System prompts
│   ├── middleware/
│   │   ├── auth.ts           # Authentication
│   │   └── error.ts          # Error handling
│   └── types/
├── public/                    # Static assets
├── package.json
└── tsconfig.json
```

### Monorepo Full-Stack

```
my-app/
├── package.json              # Root workspace config
├── packages/
│   ├── backend/
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── index.ts      # Express server
│   │   │   ├── agent.ts      # Agent logic
│   │   │   └── tools/        # Tool definitions
│   │   └── dist/
│   ├── frontend/
│   │   ├── package.json
│   │   ├── src/
│   │   └── dist/
│   └── shared/
│       ├── package.json
│       └── src/              # Shared types/utils
└── tsconfig.json             # Base config
```

## 5. Permission Modes

**CRITICAL: Standalone servers must use `bypassPermissions`**

When building standalone applications (Express servers, CLI tools), always use `'bypassPermissions'`:

```typescript
// ✅ CORRECT for standalone servers
const messages = query({
  prompt,
  options: {
    permissionMode: 'bypassPermissions',  // Always use this!
    systemPrompt,
    mcpServers,
  },
});
```

**Why?** The `'interactive'` mode requires Claude Code to be running to show permission prompts. Standalone servers run independently and cannot display interactive prompts, leading to "Claude Code process exited with code 1" errors.

```typescript
// ❌ WRONG for standalone servers
permissionMode: mode === 'execute' ? 'bypassPermissions' : 'interactive',
// This will crash when mode is 'plan'!
```

**When to use each mode:**
- `'bypassPermissions'` - Standalone servers, CLI tools, background agents
- `'interactive'` - Only when running inside Claude Code with UI for approvals
- `'allowedTools'` - When you want to restrict tool access programmatically

## 6. Best Practices

### DO

✅ **Set `type: "module"` in package.json**

✅ **Create MCP servers at query time, not module level**
```typescript
// GOOD: In function scope
async function runAgent() {
  const server = createSdkMcpServer({ tools });
  const messages = query({ options: { mcpServers: { 'name': server } } });
}
```

✅ **Use proper TypeScript configuration**
- Enable strict mode
- Use Node16 module resolution
- Generate declaration files

✅ **Authentication handled automatically by Claude Code**
- No API keys needed
- Works seamlessly within Claude Code

### DON'T

❌ **Don't mix module types**
```typescript
// package.json should have "type": "module"
// Don't mix require() and import
```

❌ **Don't use `require()` with ES modules**
```typescript
// BAD
const { query } = require('@anthropic-ai/claude-agent-sdk');

// GOOD
import { query } from '@anthropic-ai/claude-agent-sdk';
```

❌ **Don't forget .js extensions in imports**
```typescript
// BAD
import { myTool } from './tools/my-tool';

// GOOD (required for Node16 module resolution)
import { myTool } from './tools/my-tool.js';
```

## 7. Example Entry Points

### CLI Agent

```typescript
// src/index.ts
import { runAgent } from './agent.js';

async function main() {
  const prompt = process.argv.slice(2).join(' ');

  if (!prompt) {
    console.error('Usage: npm start -- <prompt>');
    process.exit(1);
  }

  await runAgent(prompt);
}

main().catch(console.error);
```

### Express Server

```typescript
// src/index.ts
import express from 'express';
import { agentRouter } from './routes/agent.js';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use('/api/agent', agentRouter);

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

## 8. Development Workflow

```bash
# Install dependencies
npm install

# Development with watch mode
npm run dev

# Type check only
npm run typecheck

# Build for production
npm run build

# Run built version
npm start
```

## 9. Testing Setup (Optional)

```json
// package.json
{
  "scripts": {
    "test": "vitest",
    "test:watch": "vitest watch"
  },
  "devDependencies": {
    "vitest": "^1.0.0"
  }
}
```

```typescript
// src/tools/__tests__/my-tool.test.ts
import { describe, it, expect } from 'vitest';
import { myTool } from '../my-tool.js';

describe('myTool', () => {
  it('should process input correctly', async () => {
    const result = await myTool.execute({ param: 'test' });
    expect(result.content[0].text).toContain('expected output');
  });
});
```

## 10. Deployment Considerations

### Environment Variables
- Store sensitive data in environment variables
- Use `.env` for local development
- Configure production environment separately

### Build Artifacts
- Always build before deploying: `npm run build`
- Deploy only the `dist/` directory and `package.json`
- Run `npm install --production` on the server

### Process Management
- Use PM2, systemd, or similar for process management
- Configure proper logging
- Set up health checks and monitoring
