# Node Discovery Reference

Complete reference for discovering and understanding n8n nodes using n8n-MCP tools.

## Getting Started

### tools_documentation
**Always start here** to get best practices and tool documentation.

```
mcp__n8n__tools_documentation
```

Returns comprehensive guidance on using all n8n-MCP tools effectively.

## Template Discovery (Check First!)

Before searching for nodes, check if a template exists. n8n-MCP has **2,709 workflow templates**.

### search_templates

**Search by Task** (Curated categories):
```
mcp__n8n__search_templates({
  searchMode: 'by_task',
  task: 'slack_integration'
})
```

Available tasks:
- `webhook_processing`
- `slack_integration`
- `email_automation`
- `data_transformation`
- `api_integration`
- And many more...

**Search by Metadata** (Smart filtering):
```
mcp__n8n__search_templates({
  searchMode: 'by_metadata',
  complexity: 'simple',           // 'simple' | 'medium' | 'complex'
  requiredService: 'openai',      // Service name
  targetAudience: 'developers',   // 'marketers' | 'developers' | 'analysts'
  maxSetupMinutes: 30             // Time filter
})
```

**Search by Nodes** (Find templates using specific nodes):
```
mcp__n8n__search_templates({
  searchMode: 'by_nodes',
  nodeTypes: ['n8n-nodes-base.slack', 'n8n-nodes-base.webhook']
})
```

**Keyword Search** (Default mode):
```
mcp__n8n__search_templates({
  query: 'slack notification webhook'
})
```

### get_template

Get complete workflow JSON from a template:

```
mcp__n8n__get_template(templateId, {
  mode: 'full'           // 'nodes_only' | 'structure' | 'full'
})
```

**Modes:**
- `nodes_only` - Just the nodes configuration
- `structure` - Nodes and connections topology
- `full` - Complete workflow JSON ready to deploy

## Node Search

### search_nodes

Full-text search across 544 n8n nodes:

```
mcp__n8n__search_nodes({
  query: 'send email gmail',
  includeExamples: true    // Returns real-world configurations
})
```

**Parameters:**
- `query` (required) - Search terms
- `includeExamples` (optional) - Include 2 example configs per node from templates

**Tips:**
- Use specific terms: "send email gmail" not just "email"
- Add `includeExamples: true` for ready-to-use configurations
- Search for triggers: "trigger webhook schedule"

### Search Patterns

**By Functionality:**
```
mcp__n8n__search_nodes({query: 'send slack message'})
mcp__n8n__search_nodes({query: 'http api request'})
mcp__n8n__search_nodes({query: 'schedule cron trigger'})
```

**By Service:**
```
mcp__n8n__search_nodes({query: 'google sheets'})
mcp__n8n__search_nodes({query: 'openai chatgpt'})
mcp__n8n__search_nodes({query: 'telegram bot'})
```

**By Type:**
```
mcp__n8n__search_nodes({query: 'trigger'})    // All triggers
mcp__n8n__search_nodes({query: 'AI agent'})   // AI nodes
mcp__n8n__search_nodes({query: 'transform'})  // Data transformation
```

## Node Details

### get_node

Unified tool for getting node information with multiple modes.

**Standard Detail (Default):**
```
mcp__n8n__get_node({
  nodeType: 'n8n-nodes-base.slack',
  detail: 'standard',
  includeExamples: true
})
```

Returns essential 10-20 properties that matter most.

**Detail Levels:**
| Level | Tokens | Use Case |
|-------|--------|----------|
| `minimal` | ~200 | Basic metadata only |
| `standard` | ~500-1000 | Essential properties (default) |
| `full` | ~3000-8000 | Complete information |

**Documentation Mode:**
```
mcp__n8n__get_node({
  nodeType: 'n8n-nodes-base.httpRequest',
  mode: 'docs'
})
```

Returns human-readable markdown documentation.

**Property Search Mode:**
```
mcp__n8n__get_node({
  nodeType: 'n8n-nodes-base.httpRequest',
  mode: 'search_properties',
  propertyQuery: 'authentication'
})
```

Find specific properties by name or description.

**Version Information:**
```
mcp__n8n__get_node({nodeType: 'n8n-nodes-base.httpRequest', mode: 'versions'})
mcp__n8n__get_node({nodeType: 'n8n-nodes-base.httpRequest', mode: 'breaking'})
mcp__n8n__get_node({nodeType: 'n8n-nodes-base.httpRequest', mode: 'migrations'})
```

## Node Type Naming

### Core Nodes
Use `n8n-nodes-base.` prefix:
```
n8n-nodes-base.httpRequest
n8n-nodes-base.webhook
n8n-nodes-base.slack
n8n-nodes-base.code
n8n-nodes-base.if
n8n-nodes-base.set
```

### LangChain/AI Nodes
Use `@n8n/n8n-nodes-langchain.` prefix:
```
@n8n/n8n-nodes-langchain.agent
@n8n/n8n-nodes-langchain.lmChatOpenAi
@n8n/n8n-nodes-langchain.toolCode
@n8n/n8n-nodes-langchain.memoryBufferWindow
```

## Popular Nodes Quick Reference

### Triggers
| Node | Purpose |
|------|---------|
| `n8n-nodes-base.webhook` | HTTP webhook trigger |
| `n8n-nodes-base.scheduleTrigger` | Cron/interval scheduling |
| `n8n-nodes-base.manualTrigger` | Manual execution |
| `n8n-nodes-base.executeWorkflowTrigger` | Sub-workflow calls |

### Data Processing
| Node | Purpose |
|------|---------|
| `n8n-nodes-base.set` | Set/transform data |
| `n8n-nodes-base.code` | JavaScript/Python code |
| `n8n-nodes-base.if` | Conditional branching |
| `n8n-nodes-base.switch` | Multi-branch routing |
| `n8n-nodes-base.merge` | Combine data streams |
| `n8n-nodes-base.splitInBatches` | Batch processing |

### External Services
| Node | Purpose |
|------|---------|
| `n8n-nodes-base.httpRequest` | HTTP API calls |
| `n8n-nodes-base.slack` | Slack integration |
| `n8n-nodes-base.googleSheets` | Google Sheets |
| `n8n-nodes-base.gmail` | Email via Gmail |
| `n8n-nodes-base.telegram` | Telegram bot |

### AI/LangChain
| Node | Purpose |
|------|---------|
| `@n8n/n8n-nodes-langchain.agent` | AI agent orchestration |
| `@n8n/n8n-nodes-langchain.lmChatOpenAi` | OpenAI chat models |
| `@n8n/n8n-nodes-langchain.toolCode` | Custom AI tools |

## Best Practices

1. **Templates First** - Always search templates before building from scratch
2. **Include Examples** - Use `includeExamples: true` for real configs
3. **Start with Standard** - Use `detail: 'standard'` before requesting full info
4. **Search Specific** - Use precise terms for better search results
5. **Check Documentation** - Use `mode: 'docs'` for human-readable guidance
6. **Parallel Execution** - Search multiple nodes simultaneously
