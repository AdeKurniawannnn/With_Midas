# AI Agent Patterns Reference

Complete reference for building AI Agent workflows in n8n using LangChain nodes.

## Overview

n8n has **271 AI-capable nodes** that can be used in AI workflows. Any node can potentially be used as an AI tool, not just those explicitly marked.

## LangChain Node Naming

LangChain/AI nodes use the `@n8n/n8n-nodes-langchain.` prefix:

```
@n8n/n8n-nodes-langchain.agent
@n8n/n8n-nodes-langchain.lmChatOpenAi
@n8n/n8n-nodes-langchain.toolCode
@n8n/n8n-nodes-langchain.memoryBufferWindow
@n8n/n8n-nodes-langchain.outputParserStructured
```

## Core AI Components

### Language Models

**OpenAI Chat:**
```
@n8n/n8n-nodes-langchain.lmChatOpenAi
```

**Anthropic Claude:**
```
@n8n/n8n-nodes-langchain.lmChatAnthropic
```

**Other Models:**
- `@n8n/n8n-nodes-langchain.lmChatOllama` - Local models
- `@n8n/n8n-nodes-langchain.lmChatGooglePalm` - Google PaLM
- `@n8n/n8n-nodes-langchain.lmChatAzureOpenAi` - Azure OpenAI

### AI Agent

The core orchestration node:
```
@n8n/n8n-nodes-langchain.agent
```

**Inputs:**
- `ai_languageModel` - Required: Language model connection
- `ai_tool` - Optional: Tool connections
- `ai_memory` - Optional: Conversation memory
- `ai_outputParser` - Optional: Structured output

### Memory Types

**Buffer Window Memory:**
```
@n8n/n8n-nodes-langchain.memoryBufferWindow
```
Keeps last N messages.

**Vector Store Memory:**
```
@n8n/n8n-nodes-langchain.memoryVectorStore
```
Semantic search over conversation history.

### Tools

**Code Tool:**
```
@n8n/n8n-nodes-langchain.toolCode
```
Custom JavaScript/Python tool.

**HTTP Tool:**
```
@n8n/n8n-nodes-langchain.toolHttpRequest
```
Make API calls as tools.

**Calculator:**
```
@n8n/n8n-nodes-langchain.toolCalculator
```

**Wikipedia:**
```
@n8n/n8n-nodes-langchain.toolWikipedia
```

## Basic AI Agent Workflow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Trigger   │────▶│   AI Agent   │────▶│   Output    │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              ┌─────────┐   ┌─────────┐
              │   LLM   │   │  Tools  │
              └─────────┘   └─────────┘
```

### Minimal Configuration

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.manualTrigger",
      "name": "Manual Trigger"
    },
    {
      "type": "@n8n/n8n-nodes-langchain.agent",
      "name": "AI Agent",
      "parameters": {
        "text": "={{ $json.query }}"
      }
    },
    {
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "name": "OpenAI Chat Model",
      "parameters": {
        "model": "gpt-4o"
      }
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [["AI Agent"]]
    },
    "OpenAI Chat Model": {
      "ai_languageModel": [["AI Agent"]]
    }
  }
}
```

## Using Any Node as AI Tool

**Key Insight:** ANY n8n node can be configured as an AI tool, not just those with `usableAsTool=true`.

### Making a Node a Tool

1. Configure the node normally
2. Set `usableAsTool: true` in node configuration
3. Connect to agent's `ai_tool` input

### Example: HTTP Request as Tool

```json
{
  "type": "n8n-nodes-base.httpRequest",
  "name": "API Tool",
  "parameters": {
    "url": "https://api.example.com/data",
    "method": "GET"
  },
  "typeVersion": 4,
  "position": [500, 300]
}
```

Connect to agent:
```json
{
  "connections": {
    "API Tool": {
      "ai_tool": [["AI Agent"]]
    }
  }
}
```

## AI Agent Validation

The n8n-MCP validates AI workflows for:

### 1. Missing Language Model
```
ERROR: AI Agent requires a connected language model
```

Every agent needs an LLM connected to `ai_languageModel`.

### 2. Tool Connection Issues
```
WARNING: Agent has no tools connected
```

While optional, tools give agents capabilities.

### 3. Streaming Constraints
```
WARNING: Streaming enabled but output node doesn't support it
```

Ensure response nodes can handle streaming.

### 4. Memory Configuration
```
INFO: Consider adding memory for multi-turn conversations
```

Memory enables conversational context.

## Advanced Patterns

### Multi-Tool Agent

```
┌─────────────┐
│   Trigger   │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│   AI Agent   │◀─── LLM
└──────────────┘
       │
  ┌────┴────┬────┬────┐
  ▼         ▼    ▼    ▼
┌────┐  ┌────┐ ┌────┐ ┌────┐
│Tool│  │Tool│ │Tool│ │Tool│
│ 1  │  │ 2  │ │ 3  │ │ 4  │
└────┘  └────┘ └────┘ └────┘
```

### Agent with Memory

```
┌─────────────┐
│   Chat      │
│   Trigger   │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│   AI Agent   │◀─── LLM
└──────────────┘◀─── Memory (Buffer Window)
       │
       ▼
┌─────────────┐
│  Response   │
└─────────────┘
```

### Structured Output

```
┌──────────────┐
│   AI Agent   │◀─── LLM
└──────────────┘◀─── Output Parser (Structured)
       │
       ▼
┌─────────────┐
│  Validated  │
│    JSON     │
└─────────────┘
```

## Chat Trigger Workflow

For conversational AI:

```json
{
  "nodes": [
    {
      "type": "n8n-nodes-base.chatTrigger",
      "name": "Chat Trigger",
      "webhookId": "chat-webhook-id"
    },
    {
      "type": "@n8n/n8n-nodes-langchain.agent",
      "name": "AI Agent"
    },
    {
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "name": "OpenAI"
    },
    {
      "type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
      "name": "Memory",
      "parameters": {
        "sessionIdType": "fromInput",
        "sessionKey": "sessionId"
      }
    }
  ]
}
```

## Best Practices

### 1. Always Connect LLM
Every AI Agent needs a language model. Validation will fail without one.

### 2. Use Memory for Conversations
For multi-turn interactions, add memory to maintain context.

### 3. Define Clear Tool Descriptions
When using tools, provide clear descriptions so the agent knows when to use them.

### 4. Handle Streaming Carefully
If enabling streaming, ensure downstream nodes support it.

### 5. Structured Output for Reliability
Use output parsers when you need consistent JSON structure.

### 6. Test Individual Tools
Before connecting to agent, test each tool node independently.

### 7. Monitor Token Usage
AI operations can be expensive. Monitor and optimize prompts.

## Common Issues

### Agent Not Using Tools
- Check tool descriptions
- Verify tool connections to `ai_tool` input
- Test tools independently

### Memory Not Working
- Verify session ID is passed correctly
- Check memory node configuration
- Ensure memory connected to `ai_memory` input

### Inconsistent Output
- Add output parser for structured responses
- Define JSON schema for expected output
- Validate responses before use

### High Latency
- Use faster models (gpt-4o-mini)
- Reduce context size
- Optimize tool selection
