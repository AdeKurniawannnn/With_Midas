# Jina AI API Endpoints Reference

This document provides complete parameter documentation for all 6 Jina AI Search Foundation APIs.

## Table of Contents

- [Reader API](#reader-api)
- [Embeddings API](#embeddings-api)
- [Reranker API](#reranker-api)
- [Classifier API](#classifier-api)
- [Segmenter API](#segmenter-api)
- [DeepSearch API](#deepsearch-api)

---

## Reader API

### Endpoints

#### URL to Markdown
- **Endpoint**: `https://r.jina.ai/http://example.com`
- **Method**: GET
- **Description**: Convert any URL to clean, LLM-friendly markdown

#### Web Search to Markdown
- **Endpoint**: `https://s.jina.ai/your-search-query`
- **Method**: GET
- **Description**: Search the web and convert results to markdown

### Parameters

#### Reader URL Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | string | None | API key for higher rate limits |
| `browser_engine` | string | "default" | Browser engine quality/speed trade-off |
| `content_format` | string | "default" | Level of detail in response |
| `json_response` | boolean | false | Return structured JSON response |
| `timeout` | integer | 30 | Maximum page load wait time (seconds) |
| `token_budget` | integer | None | Maximum tokens allowed per request |
| `use_readerlm_v2` | boolean | false | Use ReaderLM-v2 for higher quality (3x cost) |
| `css_selectors_only` | string | None | Target specific page elements |
| `css_selectors_wait_for` | string | None | Wait for CSS selectors before returning |
| `css_selectors_excluding` | string | None | Remove elements matching selectors |
| `remove_images` | boolean | false | Remove all images from response |
| `gather_links` | string | "none" | Create links section (none/all) |
| `gather_images` | string | "none" | Create images section (none/all) |
| `viewport` | string | None | Browser viewport dimensions (WxH) |
| `forward_cookie` | string | None | Forward custom cookie settings |
| `image_caption` | boolean | false | Auto-caption images with alt tags |
| `proxy_server` | string | None | Use custom proxy server |
| `country_proxy` | string | "auto" | Location-based proxy (auto/none/country) |
| `bypass_cache` | boolean | false | Ignore cached content |
| `no_cache_track` | boolean | false | Don't cache or track request |
| `github_flavored_markdown` | boolean | true | Enable GFM features |
| `stream_mode` | boolean | false | Stream mode for large pages |
| `browser_locale` | string | None | Control browser locale |
| `robots_policy` | boolean | true | Comply with robots.txt |
| `iframe_extraction` | boolean | false | Process embedded iframes |
| `shadow_dom_extraction` | boolean | false | Extract Shadow DOM content |
| `follow_redirect` | boolean | true | Follow full redirect chain |
| `eu_compliance` | boolean | false | EU jurisdiction hosting |

#### Reader Search Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | string | None | API key for higher rate limits |
| `json_response` | boolean | false | Return structured JSON response |

### Response Format

```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "content": "# Example Domain\n\nThis domain is for use...",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Rate Limits

- **No API Key**: 20 RPM (URL), Blocked (Search)
- **Standard Key**: 500 RPM (URL), 100 RPM (Search)
- **Premium Key**: 5000 RPM (URL), 1000 RPM (Search)

---

## Embeddings API

### Endpoint

- **Endpoint**: `https://api.jina.ai/v1/embeddings`
- **Method**: POST
- **Description**: Generate embeddings for text and images

### Request Body

```json
{
  "model": "jina-embeddings-v4",
  "input": ["text1", "text2"],
  "normalized": true,
  "embedding_type": "float",
  "dimensions": 1024
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | Yes | - | Embedding model name |
| `input` | array | Yes | - | Text strings or image objects |
| `normalized` | boolean | No | true | L2 normalization |
| `embedding_type` | string | No | "float" | Output format (float/binary/base64) |
| `dimensions` | integer | No | None | Custom dimension truncation |

### Available Models

| Model | Size | Context | Languages | Multimodal |
|-------|------|---------|-----------|-----------|
| `jina-embeddings-v4` | 3.8B | 32K | 89 | Yes |
| `jina-embeddings-v3` | 570M | 8K | 89 | No |
| `jina-clip-v2` | 865M | 8K | 89 | Yes |
| `jina-code-embeddings-1.5b` | 1.5B | 32K | Multilingual | No |
| `jina-code-embeddings-0.5b` | 0.5B | 32K | Multilingual | No |

### Input Formats

#### Text Input
```json
{
  "input": ["Hello world", "Another text"]
}
```

#### Image Input
```json
{
  "input": [
    {"text": "Describe this image"},
    {"url": "https://example.com/image.jpg"},
    {"bytes": "base64-encoded-image-data"}
  ]
}
```

### Response Format

```json
{
  "data": [
    {
      "object": "embedding",
      "embedding": [0.1, 0.2, 0.3, ...],
      "index": 0
    }
  ],
  "model": "jina-embeddings-v4",
  "usage": {
    "prompt_tokens": 100,
    "total_tokens": 100
  }
}
```

### Rate Limits

- **No API Key**: Blocked
- **Standard Key**: 500 RPM, 1M TPM
- **Premium Key**: 2000 RPM, 5M TPM

---

## Reranker API

### Endpoint

- **Endpoint**: `https://api.jina.ai/v1/rerank`
- **Method**: POST
- **Description**: Rerank documents by query relevance

### Request Body

```json
{
  "model": "jina-reranker-v3",
  "query": "machine learning tutorials",
  "documents": ["doc1", "doc2", "doc3"],
  "top_n": 3,
  "max_chunks_per_doc": 5
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | Yes | - | Reranker model name |
| `query` | string | Yes | - | Search query |
| `documents` | array | Yes | - | Documents to rerank |
| `top_n` | integer | No | None | Number of top results |
| `max_chunks_per_doc` | integer | No | None | Maximum chunks per document |

### Available Models

| Model | Size | Context | Features |
|-------|------|---------|----------|
| `jina-reranker-v3` | 0.6B | 131K | Latest, highest quality |
| `jina-reranker-v2-base-multilingual` | 278M | 8K | 100+ languages, function calling |
| `jina-reranker-m0` | 2.4B | 10K | Multimodal, code support |
| `jina-reranker-v1-base-en` | 137M | 8K | English only |
| `jina-reranker-v1-turbo-en` | 37.8M | 8K | Fast, English only |
| `jina-reranker-v1-tiny-en` | 33M | 8K | Smallest, English only |

### Response Format

```json
{
  "results": [
    {
      "index": 2,
      "relevance_score": 0.95,
      "document": "Document text..."
    },
    {
      "index": 0,
      "relevance_score": 0.87,
      "document": "Another document..."
    }
  ],
  "model": "jina-reranker-v3",
  "usage": {
    "prompt_tokens": 150,
    "total_tokens": 150
  }
}
```

### Rate Limits

- **No API Key**: Blocked
- **Standard Key**: 500 RPM, 1M TPM
- **Premium Key**: 2000 RPM, 5M TPM

---

## Classifier API

### Endpoints

#### Classify (Inference)
- **Endpoint**: `https://api.jina.ai/v1/classify`
- **Method**: POST
- **Description**: Classify inputs using zero-shot or trained models

#### Train Classifier
- **Endpoint**: `https://api.jina.ai/v1/train`
- **Method**: POST
- **Description**: Train a few-shot classifier

### Classification Request Body

#### Zero-Shot Classification
```json
{
  "model": "jina-embeddings-v3",
  "input": [
    {"text": "Calculate compound interest"},
    {"text": "Write a poem"}
  ],
  "labels": ["Math", "Creative"]
}
```

#### Few-Shot Classification (Using Trained Model)
```json
{
  "classifier_id": "your-classifier-id",
  "input": [
    {"text": "New example to classify"}
  ]
}
```

### Training Request Body

```json
{
  "data": [
    {"text": "Buy now!", "label": "spam"},
    {"text": "Meeting tomorrow", "label": "not_spam"}
  ],
  "model": "jina-embeddings-v3",
  "num_iters": 5
}
```

### Parameters

#### Classification Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | Zero-shot | - | Model name |
| `classifier_id` | string | Few-shot | - | Trained classifier ID |
| `input` | array | Yes | - | Text or image inputs |
| `labels` | array | Zero-shot | - | Classification labels |

#### Training Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `data` | array | Yes | - | Training examples |
| `model` | string | Yes | - | Model name |
| `num_iters` | integer | No | 5 | Training iterations |

### Input Formats

#### Text Input
```json
{
  "input": [
    {"text": "Sample text to classify"}
  ]
}
```

#### Image Input
```json
{
  "input": [
    {"image": "base64-encoded-image"}
  ]
}
```

### Response Format

```json
{
  "results": [
    {
      "text": "Calculate compound interest",
      "label": "Math",
      "confidence": 0.92
    },
    {
      "text": "Write a poem",
      "label": "Creative",
      "confidence": 0.88
    }
  ],
  "model": "jina-embeddings-v3",
  "usage": {
    "prompt_tokens": 75,
    "total_tokens": 75
  }
}
```

### Training Response

```json
{
  "id": "classifier_12345",
  "status": "training_completed",
  "model": "jina-embeddings-v3"
}
```

### Rate Limits

#### Zero-Shot Classification
- **No API Key**: Blocked
- **Standard Key**: 200 RPM, 500K TPM
- **Premium Key**: 1000 RPM, 3M TPM

#### Few-Shot Classification
- **No API Key**: Blocked
- **Standard Key**: 20 RPM, 200K TPM
- **Premium Key**: 60 RPM, 1M TPM

#### Training
- **No API Key**: Blocked
- **Standard Key**: 20 RPM, 200K TPM
- **Premium Key**: 60 RPM, 1M TPM

---

## Segmenter API

### Endpoint

- **Endpoint**: `https://api.jina.ai/v1/segment`
- **Method**: GET/POST
- **Description**: Tokenize and segment long text

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input` | string | Yes | - | Text to process |
| `return_chunks` | boolean | No | false | Return text chunks |
| `max_chunk_length` | integer | No | 1000 | Maximum chunk size |
| `token_type` | string | No | "default" | Tokenization style |

### Request Examples

#### Tokenization
```bash
GET https://api.jina.ai/v1/segment?input=Your text here
```

#### Chunking
```bash
GET https://api.jina.ai/v1/segment?input=Long text...&return_chunks=true&max_chunk_length=1000
```

#### POST Request
```json
{
  "input": "Your text here",
  "return_chunks": true,
  "max_chunk_length": 1000
}
```

### Response Format

#### Tokenization Response
```json
{
  "tokens": ["Your", "text", "here"],
  "count": 3
}
```

#### Chunking Response
```json
{
  "chunks": [
    "Your text here",
    "Another chunk"
  ],
  "count": 2
}
```

### Rate Limits

- **No API Key**: 20 RPM
- **Standard Key**: 200 RPM
- **Premium Key**: 1000 RPM

**Note**: Segmenter API is FREE - no token charges

---

## DeepSearch API

### Endpoint

- **Endpoint**: `https://deepsearch.jina.ai/v1/chat/completions`
- **Method**: POST
- **Description**: Perform comprehensive AI research with search, reading, and reasoning

### Request Body

```json
{
  "model": "jina-deepsearch-v1",
  "messages": [
    {"role": "user", "content": "Research query here"}
  ],
  "stream": true,
  "reasoning_effort": "medium",
  "budget_tokens": 500000,
  "max_attempts": 5,
  "team_size": 1,
  "no_direct_answer": false,
  "arxiv_optimized": false,
  "search_language_code": "en",
  "answer_language_code": "en",
  "boost_hostnames": ["example.com"],
  "bad_hostnames": ["spam-site.com"],
  "only_hostnames": null,
  "max_returned_urls": 10
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `model` | string | Yes | - | Model name (jina-deepsearch-v1) |
| `messages` | array | Yes | - | Conversation messages |
| `stream` | boolean | No | true | Stream response |
| `reasoning_effort` | string | No | "medium" | Quality level (low/medium/high) |
| `budget_tokens` | integer | No | None | Maximum token budget |
| `max_attempts` | integer | No | None | Maximum retry attempts |
| `team_size` | integer | No | 1 | Parallel agents |
| `no_direct_answer` | boolean | No | false | Force web search |
| `arxiv_optimized` | boolean | No | false | Academic research focus |
| `search_language_code` | string | No | "auto" | Query language |
| `answer_language_code` | string | No | "auto" | Response language |
| `boost_hostnames` | array | No | null | Priority domains |
| `bad_hostnames` | array | No | null | Excluded domains |
| `only_hostnames` | array | No | null | Exclusive domains |
| `max_returned_urls` | integer | No | null | Maximum sources |

### Message Format

```json
{
  "role": "user",
  "content": "Research query here"
}
```

#### Supported Content Types
- **Text**: Plain text content
- **Images**: WebP, PNG, JPEG (URL or base64)
- **Files**: TXT, PDF (up to 10MB)

### Streaming Response Format

```json
{
  "id": "chat_12345",
  "object": "chat.completion.chunk",
  "created": 1642652800,
  "model": "jina-deepsearch-v1",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "Research content here...",
        "type": "text"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 169670,
    "completion_tokens": 27285,
    "total_tokens": 196526
  },
  "visitedURLs": ["https://example.com"],
  "readURLs": ["https://example.com"]
}
```

### Rate Limits

- **No API Key**: Blocked
- **Standard Key**: 50 RPM
- **Premium Key**: 500 RPM

---

## Common Error Codes

| Status Code | Description | Solution |
|-------------|-------------|----------|
| 400 | Bad Request | Check parameter format |
| 401 | Unauthorized | Verify API key |
| 429 | Rate Limited | Wait and retry with backoff |
| 500 | Internal Error | Contact support |
| 502 | Bad Gateway | Retry request |
| 503 | Service Unavailable | Retry later |
| 504 | Gateway Timeout | Increase timeout |

## Authentication

All API requests (except public Reader without rate limits) require authentication:

```http
Authorization: Bearer YOUR_API_KEY
```

Get your API key at: https://jina.ai/api

## Rate Limit Headers

API responses include rate limit information:

```http
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 499
X-RateLimit-Reset: 1642652800
```

## Error Handling Best Practices

1. **Implement exponential backoff** for rate limits
2. **Monitor token usage** to avoid exceeding budgets
3. **Cache responses** where appropriate
4. **Handle streaming responses** properly for DeepSearch
5. **Validate input parameters** before sending requests
6. **Use appropriate timeouts** for different APIs