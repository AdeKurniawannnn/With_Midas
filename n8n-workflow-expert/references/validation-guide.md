# Validation Guide

Comprehensive reference for validating n8n node configurations and workflows.

## Validation Philosophy

**Core Principle:** Validate BEFORE building, validate AFTER building, never deploy unvalidated workflows.

### Multi-Level Validation Strategy

```
Level 1: validate_node (mode: 'minimal')  → Quick required fields check
Level 2: validate_node (mode: 'full')     → Comprehensive validation
Level 3: validate_workflow                → Complete workflow validation
Level 4: n8n_validate_workflow            → Post-deployment validation
```

## Node Validation

### validate_node

Unified node validation tool with multiple modes.

**Minimal Mode (Quick Check):**
```
mcp__n8n__validate_node({
  nodeType: 'n8n-nodes-base.slack',
  config: {
    resource: 'message',
    operation: 'send'
  },
  mode: 'minimal'
})
```

Fast validation (~100ms) for required fields only. Use before building.

**Full Mode (Comprehensive):**
```
mcp__n8n__validate_node({
  nodeType: 'n8n-nodes-base.slack',
  config: {
    resource: 'message',
    operation: 'send',
    select: 'channel',
    channelId: { __rl: true, value: 'C123', mode: 'id' },
    text: 'Hello World'
  },
  mode: 'full',
  profile: 'runtime'
})
```

**Validation Profiles:**
| Profile | Use Case |
|---------|----------|
| `minimal` | Quick sanity check |
| `runtime` | Full runtime validation |
| `ai-friendly` | AI-optimized validation |
| `strict` | Maximum strictness |

### Common Validation Errors

**Missing Required Fields:**
```
// ERROR: Missing 'channelId' for Slack message
{
  resource: 'message',
  operation: 'send',
  text: 'Hello'
}

// FIX: Add channelId
{
  resource: 'message',
  operation: 'send',
  select: 'channel',
  channelId: { __rl: true, value: 'C123', mode: 'id' },
  text: 'Hello'
}
```

**Default Value Trap:**
```
// WARNING: Relying on defaults causes runtime failures!

// BAD - defaults may not work
{ resource: 'message', operation: 'post' }

// GOOD - explicit configuration
{
  resource: 'message',
  operation: 'post',
  select: 'channel',
  channelId: 'C123',
  text: 'Message text'
}
```

**Invalid Operation for Resource:**
```
// ERROR: 'send' is not valid for 'channel' resource
{
  resource: 'channel',
  operation: 'send'
}

// FIX: Use valid operation
{
  resource: 'channel',
  operation: 'create'
}
```

## Workflow Validation

### validate_workflow

Complete workflow validation including structure, connections, and AI Agent checks.

```
mcp__n8n__validate_workflow(workflowJson)
```

**Validates:**
- Node configurations
- Connection topology
- Expression syntax
- AI Agent requirements:
  - Missing language model detection
  - AI tool connection validation
  - Streaming mode constraints
  - Memory and output parser checks

### Validation Response Structure

```json
{
  "valid": false,
  "errors": [
    {
      "nodeId": "slack-1",
      "field": "channelId",
      "message": "Required field missing",
      "severity": "error"
    }
  ],
  "warnings": [
    {
      "nodeId": "http-1",
      "message": "No error handling configured",
      "severity": "warning"
    }
  ],
  "suggestions": [
    {
      "nodeId": "agent-1",
      "message": "Consider adding memory for multi-turn conversations"
    }
  ]
}
```

## Expression Validation

### validate_workflow_expressions

Validates all n8n expressions in the workflow.

```
mcp__n8n__validate_workflow({
  // ... workflow with expressions
  nodes: [{
    parameters: {
      text: '={{ $json.message }}'
    }
  }]
})
```

**Common Expression Errors:**

```
// ERROR: Invalid expression syntax
{{ $json.field }}      // Missing =
$json.field            // Missing {{ }}

// CORRECT
={{ $json.field }}
```

```
// ERROR: Undefined node reference
={{ $node["NonExistent"].json.field }}

// FIX: Use correct node name
={{ $node["HTTP Request"].json.field }}
```

## Post-Deployment Validation

### n8n_validate_workflow

Validate a workflow that's already deployed to n8n.

```
mcp__n8n__n8n_validate_workflow({
  id: 'workflow-id'
})
```

### n8n_autofix_workflow

Automatically fix common workflow errors.

```
mcp__n8n__n8n_autofix_workflow({
  id: 'workflow-id'
})
```

**Auto-fixes:**
- Stale connections
- Missing node IDs
- Invalid position coordinates
- Common configuration issues

## AI Agent Validation

Special validation for AI Agent workflows:

### Missing Language Model
```
// ERROR: AI Agent has no language model connected
{
  type: '@n8n/n8n-nodes-langchain.agent',
  // No LLM connection
}

// FIX: Connect a language model
// Connect lmChatOpenAi to agent's ai_languageModel input
```

### AI Tool Connections
```
// WARNING: Agent has no tools connected
// Consider adding tools for the agent to use

// Tools connect to agent's ai_tool input
```

### Streaming Mode Constraints
```
// WARNING: Streaming enabled but response node doesn't support it
// Either disable streaming or use compatible output
```

## Validation Checklist

### Before Building
- [ ] `validate_node({mode: 'minimal'})` for each node
- [ ] All required fields present
- [ ] Valid operation for resource type
- [ ] No reliance on default values

### After Building
- [ ] `validate_workflow(workflow)` passes
- [ ] All connections valid
- [ ] Expressions syntactically correct
- [ ] AI Agent has language model (if applicable)

### After Deployment
- [ ] `n8n_validate_workflow({id})` passes
- [ ] `n8n_autofix_workflow({id})` for auto-corrections
- [ ] Test execution succeeds
- [ ] Monitor initial executions

## Best Practices

1. **Validate Incrementally** - Check each node before adding to workflow
2. **Fix Before Proceeding** - Never skip validation errors
3. **Use Runtime Profile** - `profile: 'runtime'` catches more issues
4. **Check AI Requirements** - AI workflows need special validation
5. **Test After Deploy** - Use `n8n_test_workflow` to verify
6. **Monitor Executions** - Check `n8n_executions` after deployment

## Error Resolution Patterns

### Pattern: Required Field Missing
```
1. Identify missing field from error
2. Check node documentation for field format
3. Add field with correct format
4. Re-validate
```

### Pattern: Invalid Expression
```
1. Check expression syntax (={{ ... }})
2. Verify node references exist
3. Check field path in $json
4. Use expression preview in n8n
```

### Pattern: AI Agent Issues
```
1. Ensure language model connected
2. Verify tool connections
3. Check streaming compatibility
4. Validate memory configuration
```
