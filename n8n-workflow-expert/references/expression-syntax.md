# n8n Expression Syntax Reference

Complete reference for n8n expressions used in workflow configurations.

## Expression Basics

### Syntax Format

All expressions must use the `={{ }}` format:

```
={{ expression }}
```

**Common Mistakes:**
```
// WRONG
{{ $json.field }}     // Missing =
$json.field           // Missing {{ }}
= $json.field         // Missing {{ }}

// CORRECT
={{ $json.field }}
```

## Data Access

### $json - Current Item Data

Access data from the current item:

```
={{ $json.fieldName }}
={{ $json.nested.field }}
={{ $json['field-with-dashes'] }}
={{ $json.array[0] }}
```

### $node - Access Other Nodes

Access data from specific nodes:

```
={{ $node["Node Name"].json.field }}
={{ $node["HTTP Request"].json.data.items }}
```

**Case Sensitive:** Node names must match exactly.

### $input - Previous Node Data

Access data from the immediately previous node:

```
={{ $input.first().json.field }}
={{ $input.last().json.field }}
={{ $input.all() }}
={{ $input.item.json.field }}
```

### $items - All Input Items

Work with all items:

```
={{ $items.length }}
={{ $items[0].json.field }}
={{ $items.map(item => item.json.name) }}
```

## Common Patterns

### Conditional Values

```
={{ $json.status === 'active' ? 'Yes' : 'No' }}
={{ $json.value || 'default' }}
={{ $json.items?.length ?? 0 }}
```

### String Operations

```
={{ $json.name.toUpperCase() }}
={{ $json.email.toLowerCase() }}
={{ $json.text.trim() }}
={{ $json.description.substring(0, 100) }}
={{ `Hello ${$json.name}!` }}
```

### Array Operations

```
={{ $json.items.length }}
={{ $json.items.join(', ') }}
={{ $json.items.filter(i => i.active) }}
={{ $json.items.map(i => i.name) }}
={{ $json.items.find(i => i.id === '123') }}
```

### Object Operations

```
={{ Object.keys($json) }}
={{ Object.values($json.data) }}
={{ { ...$json, newField: 'value' } }}
```

### Date/Time

```
={{ new Date().toISOString() }}
={{ new Date($json.timestamp).toLocaleDateString() }}
={{ Date.now() }}
```

## Built-in Variables

### Workflow Context

| Variable | Description |
|----------|-------------|
| `$workflow.id` | Current workflow ID |
| `$workflow.name` | Workflow name |
| `$workflow.active` | Is workflow active |

### Execution Context

| Variable | Description |
|----------|-------------|
| `$execution.id` | Current execution ID |
| `$execution.mode` | 'manual' or 'trigger' |
| `$execution.resumeUrl` | Resume URL for wait nodes |

### Environment

| Variable | Description |
|----------|-------------|
| `$env.VARIABLE_NAME` | Environment variable |
| `$now` | Current timestamp |
| `$today` | Today's date |

## Node-Specific Patterns

### Webhook Data

```
// Access webhook body
={{ $json.body }}

// Access webhook headers
={{ $json.headers['content-type'] }}

// Access query parameters
={{ $json.query.param }}
```

### HTTP Request Response

```
// Response body
={{ $json.data }}

// Response status
={{ $json.statusCode }}

// Response headers
={{ $json.headers }}
```

### Code Node Output

```
// Return single item
return { field: 'value' };

// Return multiple items
return [
  { field: 'value1' },
  { field: 'value2' }
];

// Access in next node
={{ $json.field }}
```

## Error Handling

### Safe Access

```
// Optional chaining
={{ $json.nested?.field?.value }}

// Nullish coalescing
={{ $json.field ?? 'default' }}

// Logical OR (falsy check)
={{ $json.field || 'default' }}
```

### Try-Catch in Code Node

```javascript
try {
  return { result: JSON.parse($json.data) };
} catch (error) {
  return { error: error.message };
}
```

## IF Node Conditions

### Comparison Operators

```
// Equals
={{ $json.status === 'active' }}

// Not equals
={{ $json.status !== 'inactive' }}

// Greater/Less than
={{ $json.count > 10 }}
={{ $json.price <= 100 }}

// Contains
={{ $json.tags.includes('urgent') }}
={{ $json.email.includes('@company.com') }}
```

### Logical Operators

```
// AND
={{ $json.active && $json.verified }}

// OR
={{ $json.status === 'new' || $json.status === 'pending' }}

// NOT
={{ !$json.deleted }}
```

### Type Checks

```
={{ typeof $json.field === 'string' }}
={{ Array.isArray($json.items) }}
={{ $json.value !== undefined }}
={{ $json.data !== null }}
```

## Expression Tips

### 1. Always Use ={{ }}
```
// Every expression needs this wrapper
={{ anyExpression }}
```

### 2. Check Node Names
```
// Must match exactly (case-sensitive)
={{ $node["HTTP Request"].json }}  // Correct
={{ $node["http request"].json }}  // Wrong - case mismatch
```

### 3. Handle Missing Data
```
// Use optional chaining
={{ $json.user?.profile?.name ?? 'Unknown' }}
```

### 4. Debug Expressions
```
// Use Code node to inspect data
console.log($json);
return $json;
```

### 5. Complex Logic in Code Node
```
// For complex transformations, use Code node
// instead of complicated expressions
```

## Common Errors

### "Cannot read property of undefined"
```
// Problem: Accessing nested property that doesn't exist
={{ $json.user.name }}  // user is undefined

// Solution: Optional chaining
={{ $json.user?.name }}
```

### "Node not found"
```
// Problem: Wrong node name
={{ $node["Wrong Name"].json }}

// Solution: Check exact node name in workflow
={{ $node["Correct Node Name"].json }}
```

### "Expression evaluation error"
```
// Problem: Syntax error in expression
={{ $json.field.toUpperCase }  // Missing ()

// Solution: Check syntax
={{ $json.field.toUpperCase() }}
```
