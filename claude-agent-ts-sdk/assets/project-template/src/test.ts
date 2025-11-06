/**
 * Test tools independently before using in agent
 */

import { exampleTool } from './tools/example-tool.js';

async function testExampleTool() {
  console.log('Testing example tool...\n');

  try {
    const result = await exampleTool.execute({
      message: 'hello world',
    });

    console.log('Result:', result);
    console.log('\n✅ Tool test passed');
  } catch (error: any) {
    console.error('❌ Tool test failed:', error.message);
    process.exit(1);
  }
}

// Run tests
console.log('=== Tool Tests ===\n');
await testExampleTool();
console.log('\n=== All tests passed ===');
