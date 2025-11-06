import { query, createSdkMcpServer } from '@anthropic-ai/claude-agent-sdk';
import { allTools } from './tools/index.js';
import { SYSTEM_PROMPT } from './prompts/system.js';

export async function runAgent(userPrompt: string): Promise<void> {
  console.log('User:', userPrompt);
  console.log('\nAssistant: ');

  // Create MCP server at query time
  const server = createSdkMcpServer({
    name: 'my-agent-tools',
    version: '1.0.0',
    tools: allTools,
  });

  // Query Claude with streaming
  const messages = query({
    prompt: userPrompt,
    options: {
      systemPrompt: SYSTEM_PROMPT,
      permissionMode: 'bypassPermissions',
      mcpServers: {
        'my-agent-tools': server,
      },
    },
  });

  // Process stream
  try {
    for await (const event of messages) {
      if (event.type === 'assistant') {
        const message = event.message;

        if (message.content && Array.isArray(message.content)) {
          for (const block of message.content) {
            if (block.type === 'text') {
              process.stdout.write(block.text);
            } else if (block.type === 'tool_use') {
              // Debug: Log tool calls
              console.log(`\n[Tool: ${block.name}]`);
            }
          }
        }
      } else if (event.type === 'user') {
        // Tool results - usually you don't need to display these
        // They're sent back to Claude automatically
      } else if (event.type === 'error') {
        console.error('\nError:', event.error);
      }
    }
  } catch (error: any) {
    if (error.name === 'AbortError') {
      console.log('\n\nStream aborted by user');
    } else {
      throw error;
    }
  }
}
