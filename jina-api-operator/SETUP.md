# Jina API Operator - Setup Guide

## Quick Setup

### 1. Get Your API Key
Visit https://jina.ai/api and create a free account to get your API key (10M tokens/month).

### 2. Configure Environment Variables

#### Option A: Using .env file (Recommended)
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your API key
# JINA_API_KEY=your-actual-api-key-here
```

#### Option B: Set Environment Variable
```bash
export JINA_API_KEY="your-api-key-here"
python scripts/jina_client.py
```

#### Option C: Pass API Key Directly (Not Recommended)
```python
from scripts.jina_client import JinaAPIClient

client = JinaAPIClient(api_key="your-api-key-here")
```

## Environment Variables

All configuration options are optional except `JINA_API_KEY`.

### Core Settings
- `JINA_API_KEY` - Your Jina API key (required)
- `JINA_CACHE_DIR` - Cache directory (default: `cache`)
- `JINA_TIMEOUT` - Request timeout in seconds (default: `30`)
- `JINA_MAX_RETRIES` - Retry attempts (default: `3`)

### API Model Selection
- `JINA_EMBEDDINGS_MODEL` - (default: `jina-embeddings-v4`)
- `JINA_RERANKER_MODEL` - (default: `jina-reranker-v3`)
- `JINA_CLASSIFIER_MODEL` - (default: `jina-embeddings-v3`)

### DeepSearch Configuration
- `JINA_DEEPSEARCH_BUDGET_TOKENS` - Token budget (default: `500000`)
- `JINA_DEEPSEARCH_REASONING_EFFORT` - `low|medium|high` (default: `medium`)
- `JINA_DEEPSEARCH_TEAM_SIZE` - Parallel agents (default: `2`)

## Usage Examples

### Basic Usage
```python
from scripts.jina_client import JinaAPIClient

# API key loaded from JINA_API_KEY environment variable
client = JinaAPIClient()

# Use any method
content = client.read_url("https://example.com")
embeddings = client.create_embeddings(["Hello world"])
results = client.rerank_documents("query", ["doc1", "doc2"])
```

### With Custom Configuration
```python
client = JinaAPIClient(
    api_key="your-key",  # Optional, falls back to env var
    base_timeout=60,
    max_retries=5,
    cache_dir="custom_cache"
)
```

### Token Usage Tracking
```python
# Get current token usage
usage = client.get_token_usage()
print(f"Total tokens used: {sum(usage.values())}")

# Reset counter
client.reset_token_usage()
```

## Dependencies

The script requires `python-dotenv` for environment variable loading:

```bash
pip install python-dotenv requests
```

## Security Notes

- Never commit `.env` file with actual API keys
- `.gitignore` is configured to prevent accidental commits
- Use `.env.example` as template for sharing setup instructions
- For sensitive deployments, use system environment variables instead of `.env` files

## Troubleshooting

### "Jina API key not provided" Error
1. Check `.env` file exists and has `JINA_API_KEY` set
2. Verify environment variable is exported: `echo $JINA_API_KEY`
3. Ensure API key is valid from https://jina.ai/api

### Import Error for `dotenv`
```bash
pip install python-dotenv
```

### Cache Issues
- Cache is stored in `JINA_CACHE_DIR` directory
- Delete cache folder to clear: `rm -rf cache/`
- Disable cache in `.env`: `JINA_CACHE_DIR=""`

## Support

For issues or questions:
1. Check SKILL.md for detailed API documentation
2. Review examples in references/ directory
3. Check Jina API docs at https://jina.ai/docs
