---
name: n8n-workflow-expert
description: Expert n8n automation workflow design, build, and validation assistant using n8n-MCP tools. This skill should be used when users need to create n8n workflows, automate tasks, configure integrations, validate workflow configurations, deploy to n8n instances, search for nodes, build AI agents in n8n, or troubleshoot n8n automation issues.
---

# n8n Workflow Expert

Expert assistant for n8n automation using n8n-MCP tools. Provides access to 544 nodes, 2,709 workflow templates, and comprehensive validation.

## Prerequisites

This skill requires the n8n-MCP server to be configured. Verify with:
```
mcp__n8n__tools_documentation
```

For deployment features, configure `N8N_API_URL` and `N8N_API_KEY` in MCP settings.

## Quick Start

### 1. Get Tool Documentation
```
mcp__n8n__tools_documentation
```
Returns best practices and available tool reference.

### 2. Search Templates First (2,709 available)
```
mcp__n8n__search_templates({
  searchMode: 'by_task',
  task: 'slack_integration'
})
```

### 3. Search Nodes (if no template fits)
```
mcp__n8n__search_nodes({
  query: 'send email gmail',
  includeExamples: true
})
```

### 4. Validate Before Building
```
mcp__n8n__validate_node({
  nodeType: 'n8n-nodes-base.slack',
  config: { resource: 'message', operation: 'send' },
  mode: 'minimal'
})
```

## Core Workflow Process

### Phase 1: Discovery
**ALWAYS start with**: `mcp__n8n__tools_documentation` for best practices.

**Find the right approach:**
- `mcp__n8n__search_templates({searchMode: 'by_task', task: '...'})` - Templates first!
- `mcp__n8n__search_templates({searchMode: 'by_nodes', nodeTypes: ['...']})` - By node type
- `mcp__n8n__search_nodes({query: '...', includeExamples: true})` - Node search
- Think deeply about requirements. Ask clarifying questions if unclear.

### Phase 2: Configuration
**Get node details efficiently:**
- `mcp__n8n__get_node({nodeType, detail: 'standard'})` - Essential properties (default)
- `mcp__n8n__get_node({nodeType, detail: 'minimal'})` - Basic metadata (~200 tokens)
- `mcp__n8n__get_node({nodeType, detail: 'full'})` - Complete info (~3000-8000 tokens)
- `mcp__n8n__get_node({nodeType, mode: 'docs'})` - Human-readable documentation
- `mcp__n8n__get_node({nodeType, mode: 'search_properties', propertyQuery: 'auth'})` - Find specific properties
- Show visual workflow architecture to user and ask for opinion before proceeding.

### Phase 3: Pre-Validation
**Validate BEFORE building:**
- `mcp__n8n__validate_node({nodeType, config, mode: 'minimal'})` - Quick required fields check
- `mcp__n8n__validate_node({nodeType, config, mode: 'full', profile: 'runtime'})` - Full validation
- Fix ALL validation errors before proceeding

### Phase 4: Building
**Create the workflow:**
- Use validated configurations from Phase 3
- Connect nodes with proper structure
- Add error handling where appropriate
- Use n8n expressions: `$json`, `$node["NodeName"].json`
- **NEVER trust defaults** - explicitly configure ALL parameters
- Build workflow in artifact for easy editing (unless deploying to n8n instance)

### Phase 5: Workflow Validation
**Validate complete workflow:**
- `mcp__n8n__validate_workflow(workflow)` - Complete validation including AI Agent checks
- Fix any issues found before deployment

### Phase 6: Deployment (if n8n API configured)
**Deploy to n8n instance:**
- `mcp__n8n__n8n_create_workflow(workflow)` - Deploy validated workflow
- `mcp__n8n__n8n_validate_workflow({id})` - Post-deployment validation
- `mcp__n8n__n8n_autofix_workflow({id})` - Auto-fix common errors
- `mcp__n8n__n8n_update_partial_workflow({id, operations})` - Incremental updates (80-90% token savings)
- `mcp__n8n__n8n_test_workflow({workflowId})` - Test webhook/form/chat workflows

## Key Insights

### Core Principles
1. **TEMPLATES FIRST** - Check 2,709 templates before building from scratch
2. **VALIDATE EARLY AND OFTEN** - Catch errors before they reach deployment
3. **NEVER TRUST DEFAULTS** - Explicitly configure ALL parameters
4. **USE DIFF UPDATES** - `n8n_update_partial_workflow` for 80-90% token savings
5. **ANY node can be an AI tool** - Not just those with `usableAsTool=true`
6. **SILENT EXECUTION** - Execute tools without commentary between them
7. **PARALLEL EXECUTION** - Run independent operations simultaneously

### Validation Strategy

**Before Building:**
1. `validate_node({mode: 'minimal'})` - Check required fields
2. `validate_node({mode: 'full', profile: 'runtime'})` - Full configuration validation
3. Fix all errors before proceeding

**After Building:**
1. `validate_workflow(workflow)` - Complete workflow validation
2. Includes AI Agent validation (missing LLM detection, tool connections, streaming)

**After Deployment:**
1. `n8n_validate_workflow({id})` - Validate deployed workflow
2. `n8n_autofix_workflow({id})` - Auto-fix common errors
3. `n8n_executions({action: 'list'})` - Monitor execution status

## Common Patterns

### Template-First Approach
```
// Search by task
mcp__n8n__search_templates({
  searchMode: 'by_task',
  task: 'webhook_processing'
})

// Search by metadata
mcp__n8n__search_templates({
  searchMode: 'by_metadata',
  complexity: 'simple',
  requiredService: 'slack',
  targetAudience: 'marketers'
})

// Get template
mcp__n8n__get_template(templateId, {mode: 'full'})
```

### Batch Operations (Single Call)
```
mcp__n8n__n8n_update_partial_workflow({
  id: 'workflow-id',
  operations: [
    {type: 'updateNode', nodeId: 'slack-1', changes: {...}},
    {type: 'updateNode', nodeId: 'http-1', changes: {...}},
    {type: 'cleanStaleConnections'}
  ]
})
```

### IF Node Multi-Output Routing
```
// Route to TRUE branch
{type: 'addConnection', source: 'if-node', target: 'success-handler',
 sourcePort: 'main', targetPort: 'main', branch: 'true'}

// Route to FALSE branch
{type: 'addConnection', source: 'if-node', target: 'failure-handler',
 sourcePort: 'main', targetPort: 'main', branch: 'false'}
```

## Most Popular Nodes

1. `n8n-nodes-base.code` - JavaScript/Python scripting
2. `n8n-nodes-base.httpRequest` - HTTP API calls
3. `n8n-nodes-base.webhook` - Event-driven triggers
4. `n8n-nodes-base.set` - Data transformation
5. `n8n-nodes-base.if` - Conditional routing
6. `n8n-nodes-base.manualTrigger` - Manual execution
7. `n8n-nodes-base.respondToWebhook` - Webhook responses
8. `n8n-nodes-base.scheduleTrigger` - Time-based triggers
9. `@n8n/n8n-nodes-langchain.agent` - AI agents
10. `n8n-nodes-base.googleSheets` - Spreadsheet integration

**Note:** LangChain nodes use `@n8n/n8n-nodes-langchain.` prefix, core nodes use `n8n-nodes-base.`

## Resources

### references/
Documentation loaded progressively when needed:
- **node-discovery.md** - Complete node search and discovery patterns
- **validation-guide.md** - Validation strategies and error fixing
- **deployment-operations.md** - n8n API operations reference
- **expression-syntax.md** - n8n expression patterns
- **ai-agent-patterns.md** - AI workflow and LangChain patterns

### scripts/
Helper scripts for offline operations:
- **validate_workflow_json.py** - Local JSON validation
- **generate_workflow_scaffold.py** - Template-based generation

### assets/templates/
Workflow templates (not loaded into context):
- **workflow-basic.json** - Basic workflow scaffold
- **workflow-ai-agent.json** - AI agent template
- **workflow-webhook.json** - Webhook trigger template

## Important Rules

1. **ALWAYS validate before building** - Use multi-level validation
2. **ALWAYS validate after building** - Complete workflow validation
3. **NEVER deploy unvalidated workflows** - Fix all errors first
4. **USE diff operations for updates** - 80-90% token savings
5. **STATE validation results clearly** - Report what passed/failed
6. **FIX all errors before proceeding** - Don't skip validation issues
7. **ATTRIBUTE templates** - When using templates, credit the author

## Template Attribution

When using templates from n8n.io, always include attribution:
```
This workflow is based on a template by **[author]** (@[username]).
View the original at: [url]
```
