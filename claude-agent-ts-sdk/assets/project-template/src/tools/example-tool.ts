import { tool } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';

/**
 * Example tool demonstrating the basic pattern.
 * Replace this with your actual tools.
 */
export const exampleTool = tool(
  'example_tool',
  'An example tool that processes a message and returns it in uppercase',
  z.object({
    message: z.string().describe('The message to process'),
  }).shape,
  async ({ message }) => {
    try {
      // Simulate some processing
      const result = message.toUpperCase();

      return {
        content: [{
          type: 'text' as const,
          text: JSON.stringify({
            success: true,
            original: message,
            processed: result,
            timestamp: new Date().toISOString(),
          }, null, 2),
        }],
      };
    } catch (error: any) {
      return {
        content: [{
          type: 'text' as const,
          text: JSON.stringify({
            error: true,
            message: error.message,
          }),
        }],
        isError: true,
      };
    }
  }
);
