# Coolify API Reference

Complete API documentation for Coolify self-hosted PaaS.

## Base Configuration

| Property | Value |
|----------|-------|
| Base URL | `http://217.15.164.63.sslip.io:8000/api/v1` |
| Health Endpoint | `http://217.15.164.63.sslip.io:8000/api/health` |
| Authentication | Bearer Token |
| Content-Type | `application/json` |

## Authentication

All endpoints except `/health` require Bearer token authentication:

```
Authorization: Bearer 2|c48dxnCvPaJfagRJsevoWCw9HPGFvJEQBvAWzVcTffa8b64b
```

### Token Permissions

| Permission | Description |
|------------|-------------|
| `read-only` | Read data only, no modifications (default) |
| `read:sensitive` | Read data including sensitive information |
| `view:sensitive` | View passwords, API keys, etc. |
| `*` | Full access to all resources |

---

## Endpoints by Category

### Default Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/version` | Get Coolify version |
| GET | `/health` | Health check (no auth required) |
| GET | `/enable` | Enable API |
| GET | `/disable` | Disable API |

### Servers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/servers` | List all servers |
| POST | `/servers` | Create server |
| GET | `/servers/{uuid}` | Get server details |
| PATCH | `/servers/{uuid}` | Update server |
| DELETE | `/servers/{uuid}` | Delete server |
| GET | `/servers/{uuid}/resources` | List server resources |
| GET | `/servers/{uuid}/domains` | List server domains |
| GET | `/servers/{uuid}/validate` | Validate server connection |

### Applications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/applications` | List all applications |
| POST | `/applications/public` | Create from public Git repo |
| POST | `/applications/private-github-app` | Create from private repo (GitHub App) |
| POST | `/applications/private-deploy-key` | Create from private repo (Deploy Key) |
| POST | `/applications/dockerfile` | Create from Dockerfile |
| POST | `/applications/dockerimage` | Create from Docker image |
| POST | `/applications/dockercompose` | Create from Docker Compose |
| GET | `/applications/{uuid}` | Get application details |
| PATCH | `/applications/{uuid}` | Update application |
| DELETE | `/applications/{uuid}` | Delete application |
| GET | `/applications/{uuid}/logs` | Get application logs |
| GET | `/applications/{uuid}/start` | Start application |
| GET | `/applications/{uuid}/stop` | Stop application |
| GET | `/applications/{uuid}/restart` | Restart application |
| GET | `/applications/{uuid}/deployments` | List deployments |

### Application Environment Variables

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/applications/{uuid}/envs` | List env vars |
| POST | `/applications/{uuid}/envs` | Create env var |
| PATCH | `/applications/{uuid}/envs/{env_uuid}` | Update env var |
| PATCH | `/applications/{uuid}/envs/bulk` | Bulk update env vars |
| DELETE | `/applications/{uuid}/envs/{env_uuid}` | Delete env var |

### Databases

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/databases` | List all databases |
| GET | `/databases/{uuid}` | Get database details |
| PATCH | `/databases/{uuid}` | Update database |
| DELETE | `/databases/{uuid}` | Delete database |
| POST | `/databases/postgresql` | Create PostgreSQL |
| POST | `/databases/mysql` | Create MySQL |
| POST | `/databases/mariadb` | Create MariaDB |
| POST | `/databases/mongodb` | Create MongoDB |
| POST | `/databases/redis` | Create Redis |
| POST | `/databases/keydb` | Create KeyDB |
| POST | `/databases/dragonfly` | Create DragonFly |
| POST | `/databases/clickhouse` | Create ClickHouse |
| GET | `/databases/{uuid}/start` | Start database |
| GET | `/databases/{uuid}/stop` | Stop database |
| GET | `/databases/{uuid}/restart` | Restart database |

### Database Backups

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/databases/{uuid}/backups` | List backup executions |
| PATCH | `/databases/{uuid}/backups` | Update backup config |
| DELETE | `/databases/{uuid}/backups` | Delete backup config |
| DELETE | `/databases/{uuid}/backups/{backup_uuid}` | Delete backup execution |

### Deployments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/deployments` | List all deployments |
| GET | `/deployments/{uuid}` | Get deployment details |
| GET | `/deploy?uuid={uuid}` | Deploy by application UUID |
| GET | `/deploy?tag={tag}` | Deploy by tag |

### Services (One-Click Apps)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/services` | List all services |
| POST | `/services` | Create service |
| GET | `/services/{uuid}` | Get service details |
| PATCH | `/services/{uuid}` | Update service |
| DELETE | `/services/{uuid}` | Delete service |
| GET | `/services/{uuid}/start` | Start service |
| GET | `/services/{uuid}/stop` | Stop service |
| GET | `/services/{uuid}/restart` | Restart service |

### Service Environment Variables

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/services/{uuid}/envs` | List env vars |
| POST | `/services/{uuid}/envs` | Create env var |
| PATCH | `/services/{uuid}/envs/{env_uuid}` | Update env var |
| PATCH | `/services/{uuid}/envs/bulk` | Bulk update env vars |
| DELETE | `/services/{uuid}/envs/{env_uuid}` | Delete env var |

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List all projects |
| POST | `/projects` | Create project |
| GET | `/projects/{uuid}` | Get project details |
| PATCH | `/projects/{uuid}` | Update project |
| DELETE | `/projects/{uuid}` | Delete project |
| GET | `/projects/{uuid}/environments` | List environments |
| GET | `/projects/{uuid}/{env_name}` | Get environment |
| POST | `/projects/{uuid}/environments` | Create environment |
| DELETE | `/projects/{uuid}/environments/{env_name}` | Delete environment |

### Teams

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/teams` | List all teams |
| GET | `/teams/{id}` | Get team details |
| GET | `/teams/{id}/members` | Get team members |
| GET | `/teams/current` | Get authenticated team |
| GET | `/teams/current/members` | Get current team members |

### Private Keys

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/security/keys` | List all private keys |
| POST | `/security/keys` | Create private key |
| GET | `/security/keys/{uuid}` | Get private key |
| PATCH | `/security/keys/{uuid}` | Update private key |
| DELETE | `/security/keys/{uuid}` | Delete private key |

### Resources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/resources` | List all resources |

---

## Response Schemas

### Application Object

```json
{
  "id": 0,
  "uuid": "string",
  "name": "string",
  "description": "string",
  "fqdn": "string",
  "git_repository": "string",
  "git_branch": "string",
  "git_commit_sha": "string",
  "build_pack": "string",
  "docker_registry_image_name": "string",
  "docker_registry_image_tag": "string",
  "install_command": "string",
  "build_command": "string",
  "start_command": "string",
  "ports_exposes": "string",
  "ports_mappings": "string",
  "health_check_enabled": true,
  "health_check_path": "string",
  "status": "string",
  "environment_id": 0,
  "destination_id": 0,
  "created_at": "string",
  "updated_at": "string"
}
```

### Server Object

```json
{
  "id": 0,
  "uuid": "string",
  "name": "string",
  "description": "string",
  "ip": "string",
  "user": "string",
  "port": 22,
  "proxy_type": "string",
  "settings": {
    "concurrent_builds": 0,
    "is_build_server": false,
    "is_reachable": true,
    "is_usable": true,
    "wildcard_domain": "string"
  }
}
```

### Database Object

```json
{
  "id": 0,
  "uuid": "string",
  "name": "string",
  "description": "string",
  "type": "postgresql|mysql|mariadb|mongodb|redis",
  "status": "string",
  "server_id": 0,
  "environment_id": 0,
  "created_at": "string",
  "updated_at": "string"
}
```

### Service Object

```json
{
  "id": 0,
  "uuid": "string",
  "name": "string",
  "description": "string",
  "type": "string",
  "status": "string",
  "server_id": 0,
  "environment_id": 0,
  "created_at": "string",
  "updated_at": "string"
}
```

### Project Object

```json
{
  "id": 0,
  "uuid": "string",
  "name": "string",
  "description": "string",
  "team_id": 0,
  "created_at": "string",
  "updated_at": "string"
}
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable - Validation error |
| 500 | Server Error |

---

## Error Response Format

```json
{
  "message": "Error description",
  "errors": {
    "field_name": ["Validation error message"]
  }
}
```

---

## Rate Limiting

The API does not enforce strict rate limiting for self-hosted instances, but:
- Avoid excessive polling
- Use webhooks where available
- Cache responses when appropriate

---

## Official Documentation

- **API Authorization**: https://coolify.io/docs/api-reference/authorization
- **Full API Reference**: https://coolify.io/docs/api-reference
- **LLMs Context**: https://coolify.io/docs/llms.txt
