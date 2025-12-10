# Coolify LLMs Context

Cached content from https://coolify.io/docs/llms.txt for quick reference.

## What is Coolify?

Coolify is an **open-source, self-hosted Platform as a Service (PaaS)** - an alternative to:
- Vercel
- Heroku
- Railway
- Netlify

It allows you to self-host databases, services (WordPress, Plausible Analytics, Ghost), and applications (Next.js, Nuxt.js, Remix, SvelteKit) with ease.

---

## Core Concepts

### Servers
Physical or virtual machines connected to Coolify for running resources. Can be localhost or remote servers connected via SSH.

### Resources
Anything deployable: Applications, Databases, or Services.

### Projects
Organizational containers for resources. Each project can have multiple environments.

### Environments
Logical separation within projects (e.g., production, staging, development).

### Destinations
Docker networks where resources are deployed. Support standalone Docker or Swarm clusters.

---

## Documentation Structure

### Get Started
- Introduction: Overview of Coolify as self-hosted PaaS
- Installation: Docker setup script, manual configuration
- Cloud: Managed Coolify Cloud service
- Usage: Self-hosted vs Cloud comparison
- Concepts: Core Coolify concepts explained

### Applications
- Build Packs: Nixpacks, Static, Dockerfile, Docker Compose
- Frameworks: Django, Jekyll, Laravel, Phoenix, Rails, Symfony, Next.js, Vite, Vue, Nuxt, SvelteKit
- CI/CD: GitHub, GitLab, Bitbucket, Gitea integrations

### Services (200+ One-Click Apps)
Categories include:
- **Analytics**: Plausible, Umami, PostHog, Matomo
- **Automation**: n8n, ActivePieces, Windmill
- **CMS**: WordPress, Ghost, Strapi, Directus
- **Communication**: Mattermost, Rocket.Chat, Chatwoot
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Development**: Gitea, GitLab, Code Server
- **Monitoring**: Grafana, Prometheus, Uptime Kuma
- **Storage**: Nextcloud, MinIO, Seafile
- **AI/ML**: Ollama, Open WebUI, Flowise, AnythingLLM

### Databases
Supported databases:
- PostgreSQL
- MySQL
- MariaDB
- MongoDB
- Redis
- KeyDB
- DragonFly
- ClickHouse

Features: SSL encryption, scheduled backups, S3 storage integration.

### Knowledge Base

#### Servers
- Multiple server support
- Build server configuration
- Sentinel monitoring
- Non-root user setup
- OpenSSH configuration

#### Proxy
- Traefik: Dynamic routing, SSL, load balancing
- Caddy: Alternative proxy with automatic SSL

#### Docker
- Compose support with magic environment variables
- Custom Docker commands
- Registry integration
- Swarm cluster support

#### Cloudflare Integration
- Tunnels for secure access
- Origin certificates
- Full TLS/HTTPS setup

### API Reference
- Authorization: Bearer token authentication
- Endpoints for: Applications, Databases, Deployments, GitHub Apps, Projects, Resources, Private Keys, Servers, Services, Teams

### Troubleshooting
Common issues and solutions for:
- Installation failures
- Bad Gateway errors (502)
- No Available Server errors (503)
- Gateway Timeout errors (504)
- SSL certificate issues
- Server connection problems

---

## Key URLs

| Resource | URL |
|----------|-----|
| Documentation | https://coolify.io/docs |
| LLMs Context | https://coolify.io/docs/llms.txt |
| API Reference | https://coolify.io/docs/api-reference |
| GitHub | https://github.com/coollabsio/coolify |
| Discord | https://coolify.io/discord |

---

## Quick Reference: Service Types

### Most Popular Services

| Service | Type Key | Description |
|---------|----------|-------------|
| Plausible | `plausible` | Privacy-focused analytics |
| Umami | `umami` | Simple web analytics |
| n8n | `n8n` | Workflow automation |
| Ghost | `ghost` | Publishing platform |
| WordPress | `wordpress` | CMS |
| Grafana | `grafana` | Monitoring dashboards |
| Uptime Kuma | `uptime-kuma` | Uptime monitoring |
| Nextcloud | `nextcloud` | Cloud storage |
| MinIO | `minio` | S3-compatible storage |
| Gitea | `gitea` | Git hosting |
| Ollama | `ollama` | Local LLM hosting |
| Open WebUI | `open-webui` | ChatGPT-like interface |

### Full Service List

See: https://coolify.io/docs/services/all

---

## Build Packs

| Build Pack | Description |
|------------|-------------|
| `nixpacks` | Auto-detect and build (default) |
| `static` | Static files with Nginx |
| `dockerfile` | Custom Dockerfile |
| `dockercompose` | Docker Compose stacks |

---

## Environment Variables

### Magic Variables (Docker Compose)
- `SERVICE_FQDN_*`: Generate FQDN for service
- `SERVICE_URL_*`: Generate URL for service
- `SERVICE_BASE64_*`: Base64 encoded values
- `SERVICE_PASSWORD_*`: Auto-generated passwords
- `SERVICE_USER_*`: Auto-generated usernames

### Predefined Variables
- `SOURCE_COMMIT`: Git commit SHA
- `COOLIFY_*`: System variables

---

## Health Check Configuration

```json
{
  "health_check_enabled": true,
  "health_check_path": "/",
  "health_check_port": "3000",
  "health_check_method": "GET",
  "health_check_return_code": 200,
  "health_check_interval": 5,
  "health_check_timeout": 5,
  "health_check_retries": 10,
  "health_check_start_period": 5
}
```

---

## Backup Configuration (Databases)

Supports:
- PostgreSQL (pg_dump)
- MySQL/MariaDB (mysqldump)
- MongoDB (mongodump)

Storage options:
- Local filesystem
- S3-compatible storage (AWS, R2, MinIO, Backblaze)

Cron syntax for scheduling:
- `0 0 * * *` - Daily at midnight
- `0 */6 * * *` - Every 6 hours
- `@hourly`, `@daily`, `@weekly`, `@monthly`
