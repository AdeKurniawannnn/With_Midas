# Deployment Operations Reference

Complete reference for deploying and managing n8n workflows via the n8n API.

## Prerequisites

Deployment tools require n8n API configuration:

```
N8N_API_URL=https://your-n8n-instance.com/api/v1
N8N_API_KEY=your-api-key
```

Verify connectivity:
```
mcp__n8n__n8n_health_check
```

## Workflow Management

### n8n_create_workflow

Deploy a new workflow to n8n.

```
mcp__n8n__n8n_create_workflow({
  name: 'My Workflow',
  nodes: [...],
  connections: {...},
  settings: {
    executionOrder: 'v1'
  }
})
```

**Returns:** Created workflow with ID for subsequent operations.

### n8n_get_workflow

Retrieve an existing workflow.

```
mcp__n8n__n8n_get_workflow({
  id: 'workflow-id',
  mode: 'full'           // 'full' | 'details' | 'structure' | 'minimal'
})
```

**Modes:**
| Mode | Returns |
|------|---------|
| `full` | Complete workflow JSON |
| `details` | Workflow + execution statistics |
| `structure` | Nodes and connections topology |
| `minimal` | ID, name, active status only |

### n8n_list_workflows

List workflows with filtering.

```
mcp__n8n__n8n_list_workflows({
  active: true,          // Optional: filter by status
  tags: ['production']   // Optional: filter by tags
})
```

### n8n_delete_workflow

Permanently delete a workflow.

```
mcp__n8n__n8n_delete_workflow({
  id: 'workflow-id'
})
```

## Workflow Updates

### n8n_update_full_workflow

Complete workflow replacement.

```
mcp__n8n__n8n_update_full_workflow({
  id: 'workflow-id',
  workflow: {
    name: 'Updated Workflow',
    nodes: [...],
    connections: {...}
  }
})
```

**Use when:** Making major structural changes.

### n8n_update_partial_workflow

Diff-based updates for **80-90% token savings**.

```
mcp__n8n__n8n_update_partial_workflow({
  id: 'workflow-id',
  operations: [
    {type: 'updateNode', nodeId: 'slack-1', changes: {position: [100, 200]}},
    {type: 'updateNode', nodeId: 'http-1', changes: {parameters: {...}}},
    {type: 'addConnection', source: 'node-1', target: 'node-2', sourcePort: 'main', targetPort: 'main'},
    {type: 'cleanStaleConnections'}
  ]
})
```

**Operation Types:**

| Operation | Parameters |
|-----------|------------|
| `updateNode` | `nodeId`, `changes` |
| `addNode` | `node` (complete node config) |
| `removeNode` | `nodeId` |
| `addConnection` | `source`, `target`, `sourcePort`, `targetPort`, `branch` |
| `removeConnection` | `source`, `target`, `sourcePort`, `targetPort` |
| `cleanStaleConnections` | (no params) |

### Connection Syntax

**CRITICAL:** Use four separate string parameters.

```
// CORRECT
{
  type: 'addConnection',
  source: 'source-node-id',
  target: 'target-node-id',
  sourcePort: 'main',
  targetPort: 'main'
}

// WRONG - object format
{
  type: 'addConnection',
  connection: {source: {...}, destination: {...}}
}
```

### IF Node Routing

IF nodes have two outputs (TRUE/FALSE). Use `branch` parameter:

```
// Route to TRUE branch
{
  type: 'addConnection',
  source: 'if-node',
  target: 'success-handler',
  sourcePort: 'main',
  targetPort: 'main',
  branch: 'true'
}

// Route to FALSE branch
{
  type: 'addConnection',
  source: 'if-node',
  target: 'failure-handler',
  sourcePort: 'main',
  targetPort: 'main',
  branch: 'false'
}
```

## Workflow Validation

### n8n_validate_workflow

Validate a deployed workflow.

```
mcp__n8n__n8n_validate_workflow({
  id: 'workflow-id'
})
```

### n8n_autofix_workflow

Automatically fix common errors.

```
mcp__n8n__n8n_autofix_workflow({
  id: 'workflow-id'
})
```

**Fixes:**
- Stale connections
- Missing node IDs
- Position issues
- Common misconfigurations

## Version Management

### n8n_workflow_versions

Manage version history and rollback.

```
// List versions
mcp__n8n__n8n_workflow_versions({
  id: 'workflow-id',
  action: 'list'
})

// Rollback to specific version
mcp__n8n__n8n_workflow_versions({
  id: 'workflow-id',
  action: 'rollback',
  versionId: 'version-id'
})
```

## Template Deployment

### n8n_deploy_template

Deploy a template from n8n.io directly.

```
mcp__n8n__n8n_deploy_template({
  templateId: 'template-id',
  name: 'My Deployed Template',
  autofix: true          // Auto-fix after deployment
})
```

## Execution Management

### n8n_test_workflow

Test/trigger workflow execution.

```
// Webhook workflow
mcp__n8n__n8n_test_workflow({
  workflowId: 'workflow-id',
  data: { key: 'value' },
  method: 'POST',
  headers: { 'Content-Type': 'application/json' }
})

// Chat trigger workflow
mcp__n8n__n8n_test_workflow({
  workflowId: 'workflow-id',
  message: 'Hello AI',
  sessionId: 'session-123'
})
```

**Auto-detects trigger type:** webhook, form, chat.

### n8n_executions

Manage execution history.

```
// List executions
mcp__n8n__n8n_executions({
  action: 'list',
  workflowId: 'workflow-id',
  status: 'error'        // Optional: 'success' | 'error' | 'waiting'
})

// Get execution details
mcp__n8n__n8n_executions({
  action: 'get',
  executionId: 'execution-id'
})

// Delete execution
mcp__n8n__n8n_executions({
  action: 'delete',
  executionId: 'execution-id'
})
```

## Deployment Workflow

### Recommended Process

```
1. Build & Validate Locally
   └── validate_workflow(workflowJson)

2. Deploy to n8n
   └── n8n_create_workflow(workflow)

3. Post-Deployment Validation
   └── n8n_validate_workflow({id})

4. Auto-Fix if Needed
   └── n8n_autofix_workflow({id})

5. Test Execution
   └── n8n_test_workflow({workflowId})

6. Monitor
   └── n8n_executions({action: 'list'})
```

### Update Workflow

```
1. Get Current Workflow
   └── n8n_get_workflow({id, mode: 'structure'})

2. Plan Changes
   └── Identify what needs updating

3. Use Diff Operations (Preferred)
   └── n8n_update_partial_workflow({id, operations})

4. Validate
   └── n8n_validate_workflow({id})

5. Test
   └── n8n_test_workflow({workflowId})
```

## Best Practices

1. **Validate Before Deploy** - Always run `validate_workflow` first
2. **Use Diff Updates** - 80-90% token savings with partial updates
3. **Batch Operations** - Multiple changes in single `n8n_update_partial_workflow`
4. **Test After Deploy** - Always verify with `n8n_test_workflow`
5. **Monitor Executions** - Check execution status after deployment
6. **Use Autofix** - `n8n_autofix_workflow` catches common issues
7. **Version Control** - Use `n8n_workflow_versions` for rollback capability

## Error Handling

### Deployment Failed
```
1. Check validation errors
2. Verify API connectivity (n8n_health_check)
3. Check API key permissions
4. Review workflow structure
```

### Execution Failed
```
1. Check execution details (n8n_executions get)
2. Review error messages
3. Validate node configurations
4. Test individual nodes
```

### Connection Issues
```
1. Verify N8N_API_URL is correct
2. Check API key validity
3. Ensure n8n instance is accessible
4. Run n8n_health_check
```
