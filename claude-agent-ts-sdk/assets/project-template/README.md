# My Claude Agent

A TypeScript-based Claude agent using the official `@anthropic-ai/claude-agent-sdk`.

## Setup

1. Install dependencies:
```bash
npm install
```

2. (Optional) Create `.env` if you need environment variables:
```bash
cp .env.example .env
```

3. Run in development mode:
```bash
npm run dev
```

## Usage

```bash
# Development with hot reload
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Type check
npm run typecheck

# Test tools independently
npm test
```

## Project Structure

```
my-claude-agent/
├── src/
│   ├── index.ts           # Entry point
│   ├── agent.ts           # Agent implementation
│   ├── tools/
│   │   ├── index.ts       # Tool exports
│   │   └── example-tool.ts
│   ├── prompts/
│   │   └── system.ts      # System prompts
│   └── test.ts            # Tool testing
├── package.json
├── tsconfig.json
├── .env
└── .gitignore
```

## Adding New Tools

1. Create a tool file in `src/tools/`:
```typescript
// src/tools/my-tool.ts
import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

export const myTool = tool(
  'my_tool',
  'Description of what the tool does',
  z.object({
    param: z.string().describe('Parameter description'),
  }).shape,
  async ({ param }) => {
    // Implementation
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ result: 'success' }),
      }],
    };
  }
);
```

2. Export from `src/tools/index.ts`:
```typescript
export { myTool } from './my-tool.js';
export const allTools = [myTool];
```

3. Register in agent (`src/agent.ts`)

## Development

The agent runs in development mode with hot reload. Edit files in `src/` and changes will be reflected immediately.

## Production

Build and run:
```bash
npm run build
npm start
```

## License

MIT
