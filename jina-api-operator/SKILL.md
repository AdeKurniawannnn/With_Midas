---
name: jina-api-operator
description: Comprehensive skill for operating Jina AI's complete Search Foundation platform. Use this skill when working with any of Jina's 6 core APIs: Reader (web content extraction), Embeddings (vector generation), Reranker (document reordering), Classifier (text/image classification), Segmenter (text tokenization), or DeepSearch (agentic research). This skill provides workflows, code examples, and best practices for building search, RAG, and AI applications.
---

# Jina API Operator

## Overview

This skill enables effective operation of Jina AI's complete Search Foundation ecosystem, providing unified access to 6 core APIs for building advanced search, retrieval, and AI applications. Transform general-purpose queries into specialized search workflows with concrete code examples and implementation patterns.

## Quick Start

**Setup in 5 minutes:**

1. **Get API Key**: Visit https://jina.ai/api and obtain your free API key (10M tokens)
2. **Install Dependencies**: `pip install requests aiohttp`
3. **First API Call**:
```python
import requests

# Simple web content extraction
response = requests.get('https://r.jina.ai/http://example.com')
print(response.json()['content'])
```

**When to use this skill:**
- Extracting clean content from web pages
- Generating embeddings for search/recommendation systems
- Improving search results with reranking
- Classifying text or images without training
- Processing long documents into chunks
- Performing comprehensive research with AI agents

## Reader API Operations

The Reader API converts URLs to LLM-friendly markdown, essential for web scraping and content extraction.

### Quick Start Examples

**Basic URL Reading:**
```python
import requests

# Simple URL to markdown
response = requests.get('https://r.jina.ai/http://example.com')
content = response.json()['content']
```

**Web Search with Results:**
```python
import requests

# Search and convert results
response = requests.get('https://s.jina.ai/python tutorials')
results = response.json()
```

### Advanced Features

**Content Extraction with Customization:**
```python
import requests

url = "https://r.jina.ai/http://example.com"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
params = {
    "browser_engine": "default",  # Quality vs speed
    "content_format": "default",   # Detail level control
    "json_response": "true",       # JSON output
    "timeout": 30,                 # Page load timeout
    "token_budget": 10000,         # Max tokens
    "use_readerlm_v2": "true",     # High-quality conversion (3x cost)
    "gather_links": "all",          # Extract all links
    "gather_images": "all",         # Extract all images
    "remove_images": "false",       # Remove images from response
    "viewport": "1280x720",         # Browser dimensions
    "stream_mode": "false",         # For large pages
    "github_flavored_markdown": "true",  # GFM features
    "eu_compliance": "false"        # EU hosting
}

response = requests.get(url, headers=headers, params=params)
```

### Use Cases

- **Web Scraping**: Extract clean content from any website
- **Content Processing**: Convert HTML to markdown for LLM consumption
- **Research Automation**: Batch process multiple URLs
- **Knowledge Base Building**: Create structured content from web sources

## Embedding Operations

Generate high-quality vectors for text and images using state-of-the-art embedding models.

### Quick Start Examples

**Text Embeddings:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "model": "jina-embeddings-v4",
    "input": ["Hello world", "Another text"],
    "normalized": true,
    "embedding_type": "float"
}

response = requests.post(
    "https://api.jina.ai/v1/embeddings",
    headers=headers,
    json=data
)
```

**Image Embeddings:**
```python
import requests
import base64

headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "model": "jina-embeddings-v4",
    "input": [
        {"text": "Describe this image"},
        {"url": "https://example.com/image.jpg"},
        {"bytes": "base64-encoded-image-data"}
    ],
    "normalized": true
}

response = requests.post(
    "https://api.jina.ai/v1/embeddings",
    headers=headers,
    json=data
)
```

### Advanced Configuration

**Model Selection and Parameters:**
```python
headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "model": "jina-embeddings-v4",  # Latest multimodal model
    "input": ["Your text here"],
    "normalized": true,            # L2 normalization
    "embedding_type": "float",     # float, binary, base64
    "dimensions": 1024            # Custom dimension truncation
}

# Available models:
# - jina-embeddings-v4: 3.8B, multimodal, 32K context, 2048 dimensions
# - jina-embeddings-v3: 570M, text-only, 8K context, 1024 dimensions
# - jina-clip-v2: 865M, multimodal, 8K context, 1024 dimensions
# - jina-code-embeddings-1.5b: Code-specific embeddings
```

### Use Cases

- **Semantic Search**: Build vector search engines
- **RAG Systems**: Power retrieval-augmented generation
- **Recommendation Systems**: Content-based recommendations
- **Duplicate Detection**: Find similar documents
- **Clustering**: Group related content automatically
- **Image Search**: Visual similarity matching

## Reranking Workflows

Improve search relevance by reordering documents based on query-document relationships.

### Quick Start Examples

**Basic Reranking:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "model": "jina-reranker-v3",
    "query": "machine learning tutorials",
    "documents": [
        "Introduction to machine learning algorithms",
        "Deep learning with neural networks",
        "Python programming basics",
        "Statistical methods for data analysis"
    ],
    "top_n": 3
}

response = requests.post(
    "https://api.jina.ai/v1/rerank",
    headers=headers,
    json=data
)
```

### Advanced Reranking

**Function Calling and Code Search:**
```python
headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "model": "jina-reranker-v2-base-multilingual",  # Multilingual support
    "query": "How to sort an array in Python",
    "documents": [
        "def sort_array(arr):\n    return sorted(arr)",
        "function bubble_sort(list):\n    # implementation",
        "Array sorting methods in programming languages",
        "Best practices for data structure selection"
    ],
    "top_n": 2,
    "max_chunks_per_doc": 5
}

response = requests.post(
    "https://api.jina.ai/v1/rerank",
    headers=headers,
    json=data
)
```

### Use Cases

- **Search Enhancement**: Improve initial search results
- **RAG Optimization**: Better document retrieval for generation
- **Code Search**: Find relevant code snippets
- **Multilingual Search**: Cross-language document ranking
- **Tabular Data**: Rank tables by query relevance

## Classification Tasks

Perform zero-shot and few-shot classification for text and images without model training.

### Zero-Shot Classification

**Text Classification:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "model": "jina-embeddings-v3",
    "input": [
        {"text": "Calculate compound interest on principal"},
        {"text": "Analyze ethical impacts of CRISPR gene editing"},
        {"text": "Write a poem about nature's beauty"}
    ],
    "labels": [
        "Simple task",
        "Complex reasoning",
        "Creative writing"
    ]
}

response = requests.post(
    "https://api.jina.ai/v1/classify",
    headers=headers,
    json=data
)
```

### Few-Shot Classification

**Training a Custom Classifier:**
```python
# Train classifier
headers = {"Authorization": "Bearer YOUR_API_KEY"}
train_data = {
    "data": [
        {"text": "Buy now, limited offer!", "label": "spam"},
        {"text": "Meeting tomorrow at 3pm", "label": "not_spam"},
        {"text": "Special discount just for you", "label": "spam"}
    ],
    "model": "jina-embeddings-v3",
    "num_iters": 5
}

response = requests.post(
    "https://api.jina.ai/v1/train",
    headers=headers,
    json=train_data
)
classifier_id = response.json()["id"]

# Use trained classifier
classify_data = {
    "classifier_id": classifier_id,
    "input": [{"text": "Free trial available now"}]
}

response = requests.post(
    "https://api.jina.ai/v1/classify",
    headers=headers,
    json=classify_data
)
```

### Use Cases

- **Content Moderation**: Detect inappropriate content
- **Sentiment Analysis**: Classify emotional tone
- **Intent Recognition**: Understand user goals
- **Document Categorization**: Organize content automatically
- **Image Classification**: Categorize visual content
- **Spam Detection**: Filter unwanted messages

## Segmentation Utilities

Process long text into manageable chunks and tokens for LLM consumption.

### Quick Start Examples

**Basic Tokenization:**
```python
import requests

# Simple tokenization
response = requests.get(
    "https://api.jina.ai/v1/segment",
    params={"input": "Your long text here"}
)
tokens = response.json()["tokens"]
```

**Text Chunking:**
```python
import requests

params = {
    "input": "Your very long document text...",
    "return_chunks": "true",
    "max_chunk_length": 1000
}

response = requests.get(
    "https://api.jina.ai/v1/segment",
    params=params
)
chunks = response.json()["chunks"]
```

### Advanced Features

**Custom Chunking Strategy:**
```python
params = {
    "input": long_text,
    "return_chunks": "true",
    "max_chunk_length": 2000,  # Maximum characters per chunk
    "token_type": "default"      # Tokenization style
}

# The API automatically handles:
# - Markdown structure preservation
# - HTML tag boundaries
# - LaTeX formatting
# - CJK language segmentation
# - Sentence boundaries
```

### Use Cases

- **Document Processing**: Break down long articles
- **RAG Preparation**: Create manageable chunks for retrieval
- **LLM Input Management**: Stay within model context limits
- **Cost Optimization**: Reduce token usage for long documents
- **Multilingual Processing**: Handle various writing systems

## DeepSearch Research

Perform comprehensive, iterative research with AI agents that search, read, and reason.

### Quick Start Examples

**Basic Research Query:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "model": "jina-deepsearch-v1",
    "messages": [
        {"role": "user", "content": "What are the latest developments in quantum computing?"}
    ],
    "stream": true,
    "reasoning_effort": "medium"
}

response = requests.post(
    "https://deepsearch.jina.ai/v1/chat/completions",
    headers=headers,
    json=data,
    stream=true
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### Advanced Research Configuration

**Comprehensive Research Setup:**
```python
data = {
    "model": "jina-deepsearch-v1",
    "messages": [
        {"role": "user", "content": "Comprehensive analysis of renewable energy trends"}
    ],
    "stream": true,
    "reasoning_effort": "high",      # Quality vs speed trade-off
    "budget_tokens": 500000,         # Maximum token budget
    "max_attempts": 5,               # Retry attempts
    "team_size": 2,                  # Parallel agents
    "no_direct_answer": false,       # Force web search
    "arxiv_optimized": false,        # Academic research focus
    "search_language_code": "en",    # Query language
    "answer_language_code": "en",    # Response language
    "boost_hostnames": ["arxiv.org", "nature.com"],  # Priority domains
    "bad_hostnames": ["spam-site.com"],                 # Excluded domains
    "max_returned_urls": 10         # Maximum sources
}

# Handle streaming response with citations and URLs
response = requests.post(
    "https://deepsearch.jina.ai/v1/chat/completions",
    headers=headers,
    json=data,
    stream=true
)
```

### Use Cases

- **Academic Research**: Comprehensive literature reviews
- **Market Analysis**: Industry trend investigation
- **Competitive Intelligence**: Company and product research
- **Fact-Checking**: Verify claims with multiple sources
- **Technical Documentation**: Deep dive into complex topics
- **Journalism**: Investigative research with sources

## Error Handling and Optimization

### Common Error Patterns

**Rate Limiting:**
```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

# Handle rate limits with exponential backoff
def make_api_request(url, headers=None, json_data=None):
    max_retries = 3
    base_delay = 1

    for attempt in range(max_retries):
        try:
            response = session.post(url, headers=headers, json=json_data)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                wait_time = base_delay * (2 ** attempt)
                time.sleep(wait_time)
                continue
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(base_delay * (2 ** attempt))
```

**Token Budget Management:**
```python
def estimate_tokens(text):
    """Rough token estimation (1 token ≈ 4 characters for English)"""
    return len(text) // 4

def manage_token_budget(texts, max_tokens=100000):
    """Split large requests to stay within token limits"""
    total_tokens = sum(estimate_tokens(text) for text in texts)

    if total_tokens <= max_tokens:
        return texts

    # Split into batches
    batches = []
    current_batch = []
    current_tokens = 0

    for text in texts:
        text_tokens = estimate_tokens(text)
        if current_tokens + text_tokens > max_tokens:
            if current_batch:
                batches.append(current_batch)
            current_batch = [text]
            current_tokens = text_tokens
        else:
            current_batch.append(text)
            current_tokens += text_tokens

    if current_batch:
        batches.append(current_batch)

    return batches
```

### Performance Optimization

**Caching Strategy:**
```python
import hashlib
import json
import time
from pathlib import Path

class SimpleCache:
    def __init__(self, cache_dir="cache", ttl=3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl

    def _get_cache_key(self, url, params=None, json_data=None):
        key_data = f"{url}_{str(params)}_{str(json_data)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, url, params=None, json_data=None):
        cache_key = self._get_cache_key(url, params, json_data)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            with open(cache_file) as f:
                cached_data = json.load(f)
                if time.time() - cached_data["timestamp"] < self.ttl:
                    return cached_data["response"]

        return None

    def set(self, url, response, params=None, json_data=None):
        cache_key = self._get_cache_key(url, params, json_data)
        cache_file = self.cache_dir / f"{cache_key}.json"

        cached_data = {
            "timestamp": time.time(),
            "response": response
        }

        with open(cache_file, "w") as f:
            json.dump(cached_data, f)

# Usage
cache = SimpleCache()

def cached_request(url, headers=None, params=None, json_data=None):
    # Try cache first
    cached_response = cache.get(url, params, json_data)
    if cached_response:
        return cached_response

    # Make actual request
    response = make_api_request(url, headers, params, json_data)

    # Cache the result
    cache.set(url, response.json(), params, json_data)

    return response
```

## Integration Examples

### RAG System Integration

**Complete RAG Pipeline:**
```python
import requests
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class JinaRAG:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.documents = []
        self.embeddings = []

    def add_documents(self, urls):
        """Add documents from URLs"""
        for url in urls:
            # Extract content
            content = self._extract_content(url)
            self.documents.append({"url": url, "content": content})

            # Generate embeddings
            embedding = self._generate_embedding(content)
            self.embeddings.append(embedding)

    def _extract_content(self, url):
        response = requests.get(f"https://r.jina.ai/{url}")
        return response.json()["content"]

    def _generate_embedding(self, text):
        data = {"model": "jina-embeddings-v4", "input": [text]}
        response = requests.post(
            "https://api.jina.ai/v1/embeddings",
            headers=self.headers,
            json=data
        )
        return response.json()["data"][0]["embedding"]

    def search(self, query, top_k=3):
        """Search documents with reranking"""
        # Generate query embedding
        query_embedding = self._generate_embedding(query)

        # Calculate similarities
        similarities = cosine_similarity(
            [query_embedding],
            self.embeddings
        )[0]

        # Get top documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        top_docs = [self.documents[i] for i in top_indices]

        # Rerank results
        reranked = self._rerank_documents(query, top_docs)

        return reranked

    def _rerank_documents(self, query, documents):
        data = {
            "model": "jina-reranker-v3",
            "query": query,
            "documents": [doc["content"] for doc in documents],
            "top_n": len(documents)
        }

        response = requests.post(
            "https://api.jina.ai/v1/rerank",
            headers=self.headers,
            json=data
        )

        results = response.json()["results"]

        # Reorder documents based on reranking
        reranked_docs = []
        for result in results:
            doc_index = result["index"]
            doc = documents[doc_index].copy()
            doc["relevance_score"] = result["relevance_score"]
            reranked_docs.append(doc)

        return reranked_docs

# Usage
rag = JinaRAG("your-api-key")
rag.add_documents([
    "https://example.com/article1",
    "https://example.com/article2"
])

results = rag.search("machine learning algorithms")
for result in results:
    print(f"URL: {result['url']}")
    print(f"Score: {result['relevance_score']}")
    print(f"Content: {result['content'][:200]}...")
```

### LangChain Integration

**Custom Jina Tools for LangChain:**
```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import requests

class JinaReaderTool(BaseTool):
    name = "jina_reader"
    description = "Extract clean content from web pages using Jina Reader API"

    def _run(self, url: str) -> str:
        try:
            response = requests.get(f"https://r.jina.ai/{url}")
            return response.json()["content"]
        except Exception as e:
            return f"Error extracting content: {str(e)}"

class JinaEmbeddingsTool(BaseTool):
    name = "jina_embeddings"
    description = "Generate text embeddings using Jina Embeddings API"

    def _run(self, text: str) -> list:
        headers = {"Authorization": "Bearer YOUR_API_KEY"}
        data = {
            "model": "jina-embeddings-v4",
            "input": [text],
            "normalized": True
        }

        try:
            response = requests.post(
                "https://api.jina.ai/v1/embeddings",
                headers=headers,
                json=data
            )
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            return f"Error generating embeddings: {str(e)}"

# Usage in LangChain
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI

tools = [
    Tool(name="Web Reader", func=JinaReaderTool()._run,
         description="Extract content from web pages"),
    Tool(name="Text Embeddings", func=JinaEmbeddingsTool()._run,
         description="Generate text embeddings")
]

agent = initialize_agent(tools, OpenAI(), agent="zero-shot-react-description")
result = agent.run("Extract and analyze content from https://example.com")
```

## Rate Limits and Pricing

### Understanding Rate Limits

**API Tiers and Limits:**

| API | No Key | Standard Key | Premium Key |
|-----|--------|--------------|-------------|
| Reader (URL) | 20 RPM | 500 RPM | 5000 RPM |
| Reader (Search) | Blocked | 100 RPM | 1000 RPM |
| Embeddings | Blocked | 500 RPM, 1M TPM | 2000 RPM, 5M TPM |
| Reranker | Blocked | 500 RPM, 1M TPM | 2000 RPM, 5M TPM |
| Classifier (Zero-shot) | Blocked | 200 RPM, 500K TPM | 1000 RPM, 3M TPM |
| Classifier (Few-shot) | Blocked | 20 RPM, 200K TPM | 60 RPM, 1M TPM |
| Segmenter | 20 RPM | 200 RPM | 1000 RPM |
| DeepSearch | Blocked | 50 RPM | 500 RPM |

### Cost Optimization

**Token Usage Patterns:**
- **Reader API**: Charged based on output response length
- **Search Reader**: Fixed cost starting from 10,000 tokens per request
- **Embeddings/Reranker**: Charged based on input tokens
- **DeepSearch**: Variable cost (average ~70,000 tokens per query)
- **Segmenter**: FREE - no token charges

**Budget Management:**
```python
class BudgetManager:
    def __init__(self, monthly_budget=100):
        self.monthly_budget = monthly_budget * 1_000_000  # Convert to tokens
        self.used_tokens = 0
        self.pricing = {
            "reader": 1.0,      # ~1 token per character of output
            "search": 10000,    # Fixed 10K tokens minimum
            "embeddings": 1.0,   # ~1 token per 4 characters of input
            "reranker": 1.0,     # ~1 token per 4 characters of input
            "deepsearch": 70000  # Average per query
        }

    def can_afford(self, operation, input_size=0):
        cost = self.pricing.get(operation, 0)
        if operation in ["embeddings", "reranker"]:
            cost = input_size // 4
        elif operation == "reader":
            cost = input_size

        return (self.used_tokens + cost) <= self.monthly_budget

    def track_usage(self, operation, tokens_used):
        self.used_tokens += tokens_used

    def remaining_budget(self):
        return max(0, self.monthly_budget - self.used_tokens)
```

## Resources

This skill includes specialized resources for Jina API operations:

### scripts/
Executable code for direct API operations and automation.

**jina_client.py** - Unified Python client for all 6 APIs
- Simplified authentication handling
- Automatic retry logic and error recovery
- Token usage tracking and budget management
- Streaming support for DeepSearch
- Batch processing capabilities

**Appropriate for:** Production deployments, automation scripts, API wrappers, data processing pipelines, and integration code that needs reliable execution.

### references/
Comprehensive documentation and reference material for API operations.

**api_endpoints.md** - Complete parameter documentation and examples
**rate_limits.md** - Detailed tier specifications and optimization strategies
**use_cases.md** - Real-world implementation patterns and workflows

**Appropriate for:** In-depth API documentation, integration guides, troubleshooting references, and detailed technical specifications.

### assets/
Templates and examples for API requests, responses, and configurations.

**templates/** - Ready-to-use JSON request templates for each API
**examples/** - Sample configurations for different use cases
**config/** - Default settings and environment configurations

**Appropriate for:** Development templates, testing configurations, example integrations, and starter code for new projects.