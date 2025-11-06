import { runAgent } from './agent.js';

// Get prompt from command line or use default
const userPrompt = process.argv.slice(2).join(' ') || 'Hello! What can you help me with?';

console.log('Starting agent...\n');

// Run the agent
try {
  await runAgent(userPrompt);
  console.log('\n\nAgent completed successfully');
} catch (error: any) {
  console.error('\n\nAgent error:', error.message);
  if (error.stack) {
    console.error(error.stack);
  }
  process.exit(1);
}
