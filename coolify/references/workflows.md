# Coolify Common Workflows

Step-by-step workflows for common Coolify operations.

---

## Workflow 1: Deploy Application from GitHub

### Prerequisites
- Server UUID
- Project UUID (or create one)
- GitHub repository URL

### Steps

```bash
# 1. List available servers
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/servers

# 2. List or create project
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/projects

# 3. Create application
curl -X POST \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "project_uuid": "YOUR_PROJECT_UUID",
       "server_uuid": "YOUR_SERVER_UUID",
       "environment_name": "production",
       "git_repository": "https://github.com/user/repo",
       "git_branch": "main",
       "build_pack": "nixpacks",
       "ports_exposes": "3000",
       "name": "my-nextjs-app"
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/public

# 4. Trigger deployment (if not auto-deployed)
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     "http://217.15.164.63.sslip.io:8000/api/v1/deploy?uuid=APPLICATION_UUID"

# 5. Check deployment status
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/APPLICATION_UUID/deployments
```

---

## Workflow 2: Set Up Database for Application

### Steps

```bash
# 1. Create PostgreSQL database
curl -X POST \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "server_uuid": "YOUR_SERVER_UUID",
       "project_uuid": "YOUR_PROJECT_UUID",
       "environment_name": "production",
       "name": "app-database",
       "postgres_user": "appuser",
       "postgres_password": "secure_password_here",
       "postgres_db": "appdb"
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/databases/postgresql

# 2. Get database connection details (from response)
# Internal URL: postgres://appuser:secure_password_here@app-database:5432/appdb

# 3. Add DATABASE_URL to application
curl -X POST \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "key": "DATABASE_URL",
       "value": "postgres://appuser:secure_password_here@app-database:5432/appdb",
       "is_build_time": false
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/APPLICATION_UUID/envs

# 4. Restart application to apply
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/APPLICATION_UUID/restart
```

---

## Workflow 3: Deploy One-Click Service

### Example: Deploy Plausible Analytics

```bash
# 1. Create Plausible service
curl -X POST \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "server_uuid": "YOUR_SERVER_UUID",
       "project_uuid": "YOUR_PROJECT_UUID",
       "environment_name": "production",
       "type": "plausible",
       "name": "analytics"
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/services

# 2. Get service details (includes auto-generated credentials)
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/services/SERVICE_UUID

# 3. Start the service
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/services/SERVICE_UUID/start
```

---

## Workflow 4: Configure Domain for Application

```bash
# Update application with custom domain
curl -X PATCH \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "fqdn": "https://myapp.example.com"
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/APPLICATION_UUID

# Restart to apply SSL
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/APPLICATION_UUID/restart
```

---

## Workflow 5: Set Up Database Backups

```bash
# Configure daily backup to S3
curl -X PATCH \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "enabled": true,
       "frequency": "0 2 * * *",
       "number_of_backups_to_keep": 7
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/databases/DATABASE_UUID/backups

# List backup executions
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/databases/DATABASE_UUID/backups
```

---

## Workflow 6: Create New Project with Environment

```bash
# 1. Create project
curl -X POST \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "my-saas-app",
       "description": "Production SaaS application"
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/projects

# 2. Create staging environment
curl -X POST \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "staging"
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/projects/PROJECT_UUID/environments

# 3. List environments
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/projects/PROJECT_UUID/environments
```

---

## Workflow 7: Bulk Update Environment Variables

```bash
# Update multiple env vars at once
curl -X PATCH \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "data": [
         {"key": "NODE_ENV", "value": "production"},
         {"key": "API_URL", "value": "https://api.example.com"},
         {"key": "REDIS_URL", "value": "redis://redis:6379"},
         {"key": "SECRET_KEY", "value": "your-secret-key"}
       ]
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/APPLICATION_UUID/envs/bulk
```

---

## Workflow 8: Check System Status

```bash
# 1. Health check (no auth)
curl http://217.15.164.63.sslip.io:8000/api/health

# 2. Version check
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/version

# 3. List all resources
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/resources

# 4. Validate server connection
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/servers/SERVER_UUID/validate
```

---

## Workflow 9: Rollback/Redeploy

```bash
# 1. List deployments to find previous successful one
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/APPLICATION_UUID/deployments

# 2. Trigger new deployment (uses latest commit)
curl -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     "http://217.15.164.63.sslip.io:8000/api/v1/deploy?uuid=APPLICATION_UUID"

# Note: For rollback to specific commit, update git_commit_sha then redeploy
curl -X PATCH \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{"git_commit_sha": "abc123def456"}' \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/APPLICATION_UUID
```

---

## Workflow 10: Deploy Docker Compose Stack

```bash
# Create Docker Compose application
curl -X POST \
     -H "Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b" \
     -H "Content-Type: application/json" \
     -d '{
       "project_uuid": "YOUR_PROJECT_UUID",
       "server_uuid": "YOUR_SERVER_UUID",
       "environment_name": "production",
       "git_repository": "https://github.com/user/repo",
       "git_branch": "main",
       "build_pack": "dockercompose",
       "docker_compose_location": "/docker-compose.yml",
       "name": "my-stack"
     }' \
     http://217.15.164.63.sslip.io:8000/api/v1/applications/dockercompose
```

---

## Quick Reference: Common Patterns

### Get Resource UUID from Name

```bash
# List all and parse JSON for name match
curl -H "Authorization: Bearer TOKEN" http://217.15.164.63.sslip.io:8000/api/v1/applications | \
  jq '.[] | select(.name == "my-app") | .uuid'
```

### Check if Resource is Running

```bash
curl -H "Authorization: Bearer TOKEN" http://217.15.164.63.sslip.io:8000/api/v1/applications/UUID | \
  jq '.status'
```

### Error Handling Pattern

```bash
response=$(curl -s -w "\n%{http_code}" ...)
body=$(echo "$response" | head -n -1)
code=$(echo "$response" | tail -n 1)

if [ "$code" -eq 200 ]; then
  echo "Success: $body"
else
  echo "Error ($code): $body"
fi
```
