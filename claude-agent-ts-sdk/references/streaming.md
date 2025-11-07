# Streaming and Event Handling

## Tool Execution Event Flow

When tools are executed, events follow this specific pattern that mirrors the Anthropic Messages API:

**1. `assistant` event with `tool_use` block:**

Claude requests to use a tool. The event contains:

```typescript
{
  type: 'assistant',
  message: {
    role: 'assistant',
    content: [{
      type: 'tool_use',
      id: 'toolu_01AvhNWuX3aeWaaouT5t6D73',  // Unique ID for this tool call
      name: 'mcp__server__tool_name',
      input: { param1: 'value' }
    }]
  }
}
```

**2. `user` event with `tool_result` block:**

The system/environment provides the tool result. **Note: This is a `user` event, not an `assistant` event!**

```typescript
{
  type: 'user',
  message: {
    role: 'user',
    content: [{
      type: 'tool_result',
      tool_use_id: 'toolu_01AvhNWuX3aeWaaouT5t6D73',  // References the tool_use.id
      content: [
        { type: 'text', text: '{"result": "data"}' }
      ],
      is_error: false
    }]
  }
}
```

**3. `assistant` event with text response:**

Claude processes the result and responds to the user.

```typescript
{
  type: 'assistant',
  message: {
    role: 'assistant',
    content: [{
      type: 'text',
      text: 'Based on the results...'
    }]
  }
}
```

**Key Points:**
- **Tool results come in `user` events**, not `assistant` events
- Match results using `tool_result.tool_use_id` ↔ `tool_use.id`
- Tool output is in the `content` array (usually `content[0].text`)
- This structure mirrors how you'd interact with the Anthropic API directly
- From Claude's perspective: it requests a tool (`assistant`), the world responds (`user`), then it continues (`assistant`)

## Tracking Tool Execution

```typescript
const toolExecutions = new Map();

for await (const event of messages) {
  if (event.type === 'assistant' && event.message?.content) {
    for (const block of event.message.content) {
      if (block.type === 'tool_use') {
        // Store tool execution with its ID
        toolExecutions.set(block.id, {
          name: block.name,
          input: block.input,
          status: 'running'
        });
      }
    }
  }

  if (event.type === 'user' && event.message?.content) {
    for (const block of event.message.content) {
      if (block.type === 'tool_result') {
        // Match result with the tool call
        const tool = toolExecutions.get(block.tool_use_id);
        if (tool) {
          tool.status = block.is_error ? 'error' : 'success';
          tool.output = block.content.map(c => c.text).join('\n');
        }
      }
    }
  }
}
```

## Streaming Patterns

### Pattern 1: Simple Text Streaming

```typescript
for await (const event of messages) {
  if (event.type === 'assistant') {
    for (const content of event.message.content) {
      if (content.type === 'text') {
        process.stdout.write(content.text);
      }
    }
  }
}
```

### Pattern 2: Structured Event Processing

```typescript
for await (const event of messages) {
  switch (event.type) {
    case 'assistant':
      // Handle assistant messages (including tool_use blocks)
      for (const block of event.message.content) {
        if (block.type === 'text') {
          await handleTextContent(block.text);
        } else if (block.type === 'tool_use') {
          await handleToolUse(block);
        }
      }
      break;

    case 'user':
      // Handle tool results
      for (const block of event.message.content) {
        if (block.type === 'tool_result') {
          await handleToolResult(block);
        }
      }
      break;

    case 'error':
      await handleError(event.error);
      break;
  }
}
```

### Pattern 3: Web SSE Streaming

```typescript
for await (const event of messages) {
  res.write(`data: ${JSON.stringify(event)}\n\n`);

  if (event.type === 'assistant') {
    // Optionally send custom events
    res.write(`event: message\ndata: ${JSON.stringify({
      role: 'assistant',
      content: event.message.content
    })}\n\n`);
  }
}
```

### Pattern 4: Web UI with Separate Text Sections (CRITICAL)

**Problem:** When building web UIs that display conversation with interleaved text and tools, a common mistake is accumulating ALL text into one string. This causes text from different conversation sections to merge incorrectly.

**❌ WRONG - Text accumulates forever:**
```typescript
let fullTextResponse = '';  // DON'T DO THIS

for await (const event of messages) {
  if (event.type === 'assistant' && event.message?.content) {
    for (const block of event.message.content) {
      if (block.type === 'text') {
        fullTextResponse += block.text;  // ❌ Never resets!
        // Display fullTextResponse
      }
    }
  }
}
```

This creates: `"Text1 Text2 Text3"` all merged together, even when tools appear between them.

**✅ CORRECT - Section-based text management:**
```typescript
let currentSectionText = '';  // Resets after each tool group
let contentBlocks = [];  // Structured: [text, tools, text, tools, text]
let processedToolIds = new Set();

for await (const event of messages) {
  if (event.type === 'assistant' && event.message?.content) {
    for (const block of event.message.content) {
      if (block.type === 'text') {
        // Accumulate text for CURRENT section only
        currentSectionText += block.text;

        // Update or create text block for this section
        let textBlockIndex = contentBlocks.findIndex((b, i) => {
          if (b.type === 'text') {
            // Find last text block (no tools after it)
            const hasToolsAfter = contentBlocks.slice(i + 1).some(cb => cb.type === 'tools');
            return !hasToolsAfter;
          }
          return false;
        });

        if (textBlockIndex >= 0) {
          contentBlocks[textBlockIndex].text = currentSectionText;
        } else {
          contentBlocks.push({ type: 'text', text: currentSectionText });
        }

      } else if (block.type === 'tool_use') {
        // Only process if not duplicate
        if (!processedToolIds.has(block.id)) {
          processedToolIds.add(block.id);

          // Finalize current text section
          if (currentSectionText.trim()) {
            const lastBlock = contentBlocks[contentBlocks.length - 1];
            if (lastBlock?.type === 'text') {
              lastBlock.text = currentSectionText;
            }
          }

          // RESET for next section - this is the key!
          currentSectionText = '';

          // Add tool to tools block
          // (implementation depends on your UI structure)
        }
      }
    }
  }
}
```

**Result:** Properly separated structure:
```javascript
contentBlocks = [
  { type: 'text', text: 'I will scaffold your site...' },
  { type: 'tools', tools: [scaffoldTool] },
  { type: 'text', text: 'Now I will read the files...' },
  { type: 'tools', tools: [readTool1, readTool2] },
  { type: 'text', text: 'I have updated your files...' }
]
```

**Key Principles:**
1. **Reset `currentSectionText` after tools** - Don't accumulate across tool boundaries
2. **Deduplicate tools** - Use a Set to track processed tool IDs
3. **Separate text and tool blocks** - Create structured sections, not one giant text blob
4. **Update the current text block** - Don't create a new text block on every streaming chunk

## Error Handling

### Stream Error Handling

```typescript
try {
  for await (const event of messages) {
    // Process events
  }
} catch (error) {
  if (error.name === 'AbortError') {
    console.log('Stream aborted by user');
  } else if (error.status === 429) {
    console.error('Rate limit exceeded. Please wait and retry.');
  } else {
    console.error('Agent error:', error.message);
  }
}
```

## Debugging Tips

### 1. Enable Verbose Logging

```typescript
const messages = query({
  prompt,
  options: {
    systemPrompt,
    mcpServers,
    // Add debugging
    onToolCall: (toolName, params) => {
      console.log(`[TOOL CALL] ${toolName}`, params);
    },
    onToolResult: (toolName, result) => {
      console.log(`[TOOL RESULT] ${toolName}`, result);
    },
  },
});
```

### 2. Validate Tool Definitions

```typescript
// Add validation helper
function validateTools(tools: any[]) {
  for (const t of tools) {
    if (!t.name) console.error('Tool missing name:', t);
    if (!t.description) console.error('Tool missing description:', t);
    if (!t.inputSchema) console.error('Tool missing schema:', t);
  }
}
```

### 3. Test Tools Independently

```typescript
// Test tools before using in agent
async function testTool() {
  const result = await myTool.execute({ param1: 'test' });
  console.log('Tool result:', result);
}
```
