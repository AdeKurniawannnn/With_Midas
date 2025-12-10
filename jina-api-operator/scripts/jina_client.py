#!/usr/bin/env python3
"""
Unified Jina AI Client - Complete interface to all 6 Jina Search Foundation APIs

This client provides unified access to:
- Reader API: Web content extraction
- Embeddings API: Vector generation for text/images
- Reranker API: Document relevance reordering
- Classifier API: Zero-shot and few-shot classification
- Segmenter API: Text tokenization and chunking
- DeepSearch API: Agentic research and investigation

Features:
- Automatic retry logic and error handling
- Token usage tracking and budget management
- Streaming support for DeepSearch
- Batch processing capabilities
- Comprehensive logging and monitoring
"""

import requests
import json
import time
import hashlib
import logging
import os
from typing import Dict, List, Optional, Union, Any, Iterator
from pathlib import Path
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv
import base64

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from parent directories for flexibility
    load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JinaAPIClient:
    """
    Unified client for Jina AI's complete Search Foundation platform.

    Args:
        api_key (str, optional): Your Jina AI API key. If not provided, loads from JINA_API_KEY env var
        base_timeout (int): Default timeout for API requests (default: 30)
        max_retries (int): Maximum number of retry attempts (default: 3)
        cache_dir (str): Directory for response caching (default: "cache")

    Environment Variables:
        JINA_API_KEY: API key (required if api_key not provided)
        JINA_TIMEOUT: Default timeout in seconds
        JINA_MAX_RETRIES: Maximum retry attempts
        JINA_CACHE_DIR: Cache directory path
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        cache_dir: Optional[str] = None
    ):
        # Load environment variables fresh in case .env was just created
        from pathlib import Path
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True)

        # Use provided values or fall back to environment variables
        self.api_key = api_key or os.getenv("JINA_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Jina API key not provided. Please either:\n"
                "1. Pass api_key parameter: JinaAPIClient(api_key='your-key')\n"
                "2. Set JINA_API_KEY environment variable\n"
                "3. Create a .env file in the skill root with JINA_API_KEY=your-key"
            )

        self.base_timeout = base_timeout or int(os.getenv("JINA_TIMEOUT", "30"))
        self.max_retries = max_retries or int(os.getenv("JINA_MAX_RETRIES", "3"))
        self.cache_dir = Path(cache_dir or os.getenv("JINA_CACHE_DIR", "cache"))
        self.cache_dir.mkdir(exist_ok=True)

        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        # Token usage tracking
        self.token_usage = {
            "reader": 0,
            "search": 0,
            "embeddings": 0,
            "reranker": 0,
            "classifier": 0,
            "deepsearch": 0
        }

        # API endpoints
        self.endpoints = {
            "reader_url": "https://r.jina.ai",
            "reader_search": "https://s.jina.ai",
            "embeddings": "https://api.jina.ai/v1/embeddings",
            "reranker": "https://api.jina.ai/v1/rerank",
            "classifier": "https://api.jina.ai/v1/classify",
            "train_classifier": "https://api.jina.ai/v1/train",
            "segmenter": "https://api.jina.ai/v1/segment",
            "deepsearch": "https://deepsearch.jina.ai/v1/chat/completions"
        }

        # Setup headers with the loaded API key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling and retry logic."""
        try:
            response = self.session.request(method, url, timeout=self.base_timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def _get_cache_key(self, url: str, params: Dict = None, json_data: Dict = None) -> str:
        """Generate cache key for request."""
        key_data = f"{url}_{str(params)}_{str(json_data)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cached_response(self, cache_key: str, ttl: int = 3600) -> Optional[Dict]:
        """Get cached response if available and not expired."""
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                    if time.time() - cached_data["timestamp"] < ttl:
                        return cached_data["response"]
            except (json.JSONDecodeError, KeyError):
                pass

        return None

    def _cache_response(self, cache_key: str, response: Dict):
        """Cache API response."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        cached_data = {
            "timestamp": time.time(),
            "response": response
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(cached_data, f)
        except (IOError, json.JSONDecodeError):
            logger.warning(f"Failed to cache response for key: {cache_key}")

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters for English)."""
        return len(text) // 4

    def _track_token_usage(self, api_name: str, tokens: int):
        """Track token usage for cost management."""
        self.token_usage[api_name] += tokens
        logger.info(f"Token usage - {api_name}: {self.token_usage[api_name]} (total: {sum(self.token_usage.values())})")

    # Reader API Methods
    def read_url(self, url: str, use_cache: bool = True, **params) -> Dict:
        """
        Extract content from a URL using Reader API.

        Args:
            url (str): URL to extract content from
            use_cache (bool): Whether to use cached responses
            **params: Additional parameters for content extraction

        Returns:
            Dict: Extracted content and metadata
        """
        endpoint = f"{self.endpoints['reader_url']}/{url}"
        cache_key = self._get_cache_key(endpoint, params) if use_cache else None

        # Try cache first
        if use_cache and cache_key:
            cached_response = self._get_cached_response(cache_key, ttl=3600)
            if cached_response:
                return cached_response

        # Make request
        try:
            response = self._make_request("GET", endpoint, headers=self.headers, params=params)

            # Reader API returns plain text/markdown
            content = response.text

            # Wrap in dict for consistency
            result = {'content': content, 'url': url}

            # Track token usage
            estimated_tokens = self._estimate_tokens(content)
            self._track_token_usage('reader', estimated_tokens)

            # Cache response
            if use_cache and cache_key:
                self._cache_response(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Failed to read URL {url}: {e}")
            raise

    def search_web(self, query: str, use_cache: bool = False) -> Dict:
        """
        Search the web and convert results to markdown.

        Args:
            query (str): Search query
            use_cache (bool): Whether to use cached responses

        Returns:
            Dict: Search results in markdown format
        """
        endpoint = f"{self.endpoints['reader_search']}/{query}"
        cache_key = self._get_cache_key(endpoint) if use_cache else None

        # Try cache first
        if use_cache and cache_key:
            cached_response = self._get_cached_response(cache_key, ttl=1800)  # 30 min cache
            if cached_response:
                return cached_response

        try:
            response = self._make_request("GET", endpoint, headers=self.headers)

            # Search API returns plain text (markdown), not JSON
            content = response.text

            # Wrap in dict for consistency
            result = {'content': content}

            # Track token usage (fixed cost for search)
            self._track_token_usage('search', 10000)  # Minimum 10K tokens

            # Cache response
            if use_cache and cache_key:
                self._cache_response(cache_key, result)

            return result

        except Exception as e:
            logger.error(f"Failed to search web for '{query}': {e}")
            raise

    # Embeddings API Methods
    def create_embeddings(self, texts: List[str], model: str = "jina-embeddings-v4",
                          normalized: bool = True, embedding_type: str = "float",
                          dimensions: Optional[int] = None) -> List[List[float]]:
        """
        Generate embeddings for text inputs.

        Args:
            texts (List[str]): Text strings to embed
            model (str): Model name
            normalized (bool): Whether to normalize embeddings
            embedding_type (str): Output format (float, binary, base64)
            dimensions (int): Custom dimension truncation

        Returns:
            List[List[float]]: Embedding vectors
        """
        data = {
            "model": model,
            "input": texts,
            "normalized": normalized,
            "embedding_type": embedding_type
        }

        if dimensions:
            data["dimensions"] = dimensions

        try:
            response = self._make_request("POST", self.endpoints['embeddings'],
                                         headers=self.headers, json=data)
            result = response.json()

            # Track token usage
            total_chars = sum(len(text) for text in texts)
            estimated_tokens = self._estimate_tokens(total_chars)
            self._track_token_usage('embeddings', estimated_tokens)

            return [item["embedding"] for item in result["data"]]

        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise

    def create_image_embeddings(self, images: List[Dict[str, str]],
                               model: str = "jina-embeddings-v4",
                               normalized: bool = True) -> List[List[float]]:
        """
        Generate embeddings for image inputs.

        Args:
            images (List[Dict]): List of image inputs with 'url' or 'bytes' keys
            model (str): Model name
            normalized (bool): Whether to normalize embeddings

        Returns:
            List[List[float]]: Image embedding vectors
        """
        data = {
            "model": model,
            "input": images,
            "normalized": normalized
        }

        try:
            response = self._make_request("POST", self.endpoints['embeddings'],
                                         headers=self.headers, json=data)
            result = response.json()

            # Track token usage (images cost more)
            self._track_token_usage('embeddings', len(images) * 4000)  # Rough estimate

            return [item["embedding"] for item in result["data"]]

        except Exception as e:
            logger.error(f"Failed to create image embeddings: {e}")
            raise

    # Reranker API Methods
    def rerank_documents(self, query: str, documents: List[str],
                        model: str = "jina-reranker-v3", top_n: Optional[int] = None,
                        max_chunks_per_doc: Optional[int] = None) -> List[Dict]:
        """
        Rerank documents based on query relevance.

        Args:
            query (str): Search query
            documents (List[str]): Documents to rerank
            model (str): Reranker model name
            top_n (int): Number of top results to return
            max_chunks_per_doc (int): Maximum chunks per document

        Returns:
            List[Dict]: Reranked results with relevance scores
        """
        data = {
            "model": model,
            "query": query,
            "documents": documents
        }

        if top_n is not None:
            data["top_n"] = top_n
        if max_chunks_per_doc is not None:
            data["max_chunks_per_doc"] = max_chunks_per_doc

        try:
            response = self._make_request("POST", self.endpoints['reranker'],
                                         headers=self.headers, json=data)
            result = response.json()

            # Track token usage
            total_chars = len(query) + sum(len(doc) for doc in documents)
            estimated_tokens = self._estimate_tokens(total_chars)
            self._track_token_usage('reranker', estimated_tokens)

            return result["results"]

        except Exception as e:
            logger.error(f"Failed to rerank documents: {e}")
            raise

    # Classifier API Methods
    def classify_zero_shot(self, inputs: List[Dict[str, str]], labels: List[str],
                          model: str = "jina-embeddings-v3") -> List[Dict]:
        """
        Perform zero-shot classification.

        Args:
            inputs (List[Dict]): List of inputs with 'text' or 'image' keys
            labels (List[str]): Classification labels
            model (str): Model name

        Returns:
            List[Dict]: Classification results
        """
        data = {
            "model": model,
            "input": inputs,
            "labels": labels
        }

        try:
            response = self._make_request("POST", self.endpoints['classifier'],
                                         headers=self.headers, json=data)
            result = response.json()

            # Track token usage
            input_chars = sum(len(item.get('text', '')) for item in inputs)
            label_chars = sum(len(label) for label in labels)
            estimated_tokens = self._estimate_tokens(input_chars + label_chars)
            self._track_token_usage('classifier', estimated_tokens)

            return result["results"]

        except Exception as e:
            logger.error(f"Failed to perform zero-shot classification: {e}")
            raise

    def train_classifier(self, training_data: List[Dict[str, str]],
                         model: str = "jina-embeddings-v3", num_iters: int = 5) -> str:
        """
        Train a few-shot classifier.

        Args:
            training_data (List[Dict]): Training examples with 'text' and 'label' keys
            model (str): Model name
            num_iters (int): Number of training iterations

        Returns:
            str: Classifier ID for future use
        """
        data = {
            "data": training_data,
            "model": model,
            "num_iters": num_iters
        }

        try:
            response = self._make_request("POST", self.endpoints['train_classifier'],
                                         headers=self.headers, json=data)
            result = response.json()

            # Track token usage
            input_chars = sum(len(item.get('text', '')) for item in training_data)
            estimated_tokens = self._estimate_tokens(input_chars) * num_iters
            self._track_token_usage('classifier', estimated_tokens)

            return result["id"]

        except Exception as e:
            logger.error(f"Failed to train classifier: {e}")
            raise

    def classify_with_trained(self, classifier_id: str, inputs: List[Dict[str, str]]) -> List[Dict]:
        """
        Classify inputs using a trained classifier.

        Args:
            classifier_id (str): ID of trained classifier
            inputs (List[Dict]): Inputs to classify

        Returns:
            List[Dict]: Classification results
        """
        data = {
            "classifier_id": classifier_id,
            "input": inputs
        }

        try:
            response = self._make_request("POST", self.endpoints['classifier'],
                                         headers=self.headers, json=data)
            result = response.json()

            # Track token usage
            input_chars = sum(len(item.get('text', '')) for item in inputs)
            estimated_tokens = self._estimate_tokens(input_chars)
            self._track_token_usage('classifier', estimated_tokens)

            return result["results"]

        except Exception as e:
            logger.error(f"Failed to classify with trained model: {e}")
            raise

    # Segmenter API Methods
    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenize text into individual tokens.

        Args:
            text (str): Text to tokenize

        Returns:
            List[str]: List of tokens
        """
        params = {"input": text}

        try:
            response = self._make_request("GET", self.endpoints['segmenter'], params=params)
            result = response.json()
            return result["tokens"]

        except Exception as e:
            logger.error(f"Failed to tokenize text: {e}")
            raise

    def chunk_text(self, text: str, max_chunk_length: int = 1000) -> List[str]:
        """
        Chunk text into smaller segments.

        Args:
            text (str): Text to chunk
            max_chunk_length (int): Maximum characters per chunk

        Returns:
            List[str]: List of text chunks
        """
        params = {
            "input": text,
            "return_chunks": "true",
            "max_chunk_length": max_chunk_length
        }

        try:
            response = self._make_request("GET", self.endpoints['segmenter'], params=params)
            result = response.json()
            return result["chunks"]

        except Exception as e:
            logger.error(f"Failed to chunk text: {e}")
            raise

    # DeepSearch API Methods
    def deepsearch(self, messages: List[Dict[str, str]], stream: bool = True,
                   reasoning_effort: str = "medium", budget_tokens: Optional[int] = None,
                   max_attempts: Optional[int] = None, team_size: Optional[int] = None,
                   **kwargs) -> Union[Dict, Iterator[str]]:
        """
        Perform comprehensive research using DeepSearch.

        Args:
            messages (List[Dict]): Conversation messages
            stream (bool): Whether to stream response
            reasoning_effort (str): Quality level (low/medium/high)
            budget_tokens (int): Maximum token budget
            max_attempts (int): Maximum retry attempts
            team_size (int): Number of parallel agents
            **kwargs: Additional DeepSearch parameters

        Returns:
            Union[Dict, Iterator[str]]: Research results or streaming response
        """
        data = {
            "model": "jina-deepsearch-v1",
            "messages": messages,
            "stream": stream,
            "reasoning_effort": reasoning_effort
        }

        # Add optional parameters
        if budget_tokens is not None:
            data["budget_tokens"] = budget_tokens
        if max_attempts is not None:
            data["max_attempts"] = max_attempts
        if team_size is not None:
            data["team_size"] = team_size

        data.update(kwargs)

        try:
            if stream:
                return self._stream_deepsearch(data)
            else:
                response = self._make_request("POST", self.endpoints['deepsearch'],
                                             headers=self.headers, json=data)
                result = response.json()

                # Track token usage
                usage = result.get("usage", {})
                total_tokens = usage.get("total_tokens", 0)
                self._track_token_usage('deepsearch', total_tokens)

                return result

        except Exception as e:
            logger.error(f"Failed to perform DeepSearch: {e}")
            raise

    def _stream_deepsearch(self, data: Dict) -> Iterator[str]:
        """Handle streaming DeepSearch response."""
        try:
            response = self._make_request("POST", self.endpoints['deepsearch'],
                                         headers=self.headers, json=data, stream=True)

            total_tokens = 0

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[6:]  # Remove 'data: ' prefix
                        try:
                            chunk_data = json.loads(json_str)
                            if 'usage' in chunk_data:
                                total_tokens = chunk_data['usage'].get('total_tokens', 0)
                        except json.JSONDecodeError:
                            pass

                    yield decoded_line

            # Track token usage after streaming completes
            if total_tokens > 0:
                self._track_token_usage('deepsearch', total_tokens)

        except Exception as e:
            logger.error(f"Failed to stream DeepSearch: {e}")
            raise

    # Utility Methods
    def get_token_usage(self) -> Dict[str, int]:
        """Get current token usage statistics."""
        return self.token_usage.copy()

    def reset_token_usage(self):
        """Reset token usage tracking."""
        for key in self.token_usage:
            self.token_usage[key] = 0

    def get_rate_limit_info(self) -> Dict[str, Dict]:
        """
        Get rate limit information for each API.

        Returns:
            Dict: Rate limit information per API tier
        """
        return {
            "reader_url": {
                "no_key": "20 RPM",
                "standard": "500 RPM",
                "premium": "5000 RPM"
            },
            "reader_search": {
                "no_key": "Blocked",
                "standard": "100 RPM",
                "premium": "1000 RPM"
            },
            "embeddings": {
                "no_key": "Blocked",
                "standard": "500 RPM, 1M TPM",
                "premium": "2000 RPM, 5M TPM"
            },
            "reranker": {
                "no_key": "Blocked",
                "standard": "500 RPM, 1M TPM",
                "premium": "2000 RPM, 5M TPM"
            },
            "classifier": {
                "zero_shot": {
                    "no_key": "Blocked",
                    "standard": "200 RPM, 500K TPM",
                    "premium": "1000 RPM, 3M TPM"
                },
                "few_shot": {
                    "no_key": "Blocked",
                    "standard": "20 RPM, 200K TPM",
                    "premium": "60 RPM, 1M TPM"
                }
            },
            "segmenter": {
                "no_key": "20 RPM",
                "standard": "200 RPM",
                "premium": "1000 RPM"
            },
            "deepsearch": {
                "no_key": "Blocked",
                "standard": "50 RPM",
                "premium": "500 RPM"
            }
        }


# Example usage and convenience functions
def main():
    """Example usage of JinaAPIClient."""

    # Initialize client - API key loaded from environment or .env file
    # You can also pass it directly: JinaAPIClient(api_key="your-key")
    client = JinaAPIClient()

    try:
        # Example 1: Read a URL
        print("=== Reading URL ===")
        content = client.read_url("https://example.com")
        print(f"Content length: {len(content.get('content', ''))}")

        # Example 2: Create embeddings
        print("\n=== Creating Embeddings ===")
        texts = ["Hello world", "Machine learning is fascinating"]
        embeddings = client.create_embeddings(texts)
        print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")

        # Example 3: Rerank documents
        print("\n=== Reranking Documents ===")
        query = "python programming"
        documents = [
            "Python tutorial for beginners",
            "Advanced Java programming",
            "Machine learning with Python",
            "Web development with JavaScript"
        ]
        reranked = client.rerank_documents(query, documents, top_n=2)
        print(f"Top result: {reranked[0]['text']} (score: {reranked[0]['relevance_score']})")

        # Example 4: Zero-shot classification
        print("\n=== Zero-shot Classification ===")
        inputs = [{"text": "I love this product!"}, {"text": "This is terrible."}]
        labels = ["positive", "negative"]
        results = client.classify_zero_shot(inputs, labels)
        for result in results:
            print(f"Input: {result['text']} -> {result['label']} (confidence: {result['confidence']})")

        # Example 5: Text chunking
        print("\n=== Text Chunking ===")
        long_text = "This is a very long text that needs to be chunked..." * 10
        chunks = client.chunk_text(long_text, max_chunk_length=100)
        print(f"Created {len(chunks)} chunks")

        # Example 6: Token usage
        print("\n=== Token Usage ===")
        usage = client.get_token_usage()
        total = sum(usage.values())
        print(f"Total tokens used: {total}")
        for api, tokens in usage.items():
            print(f"{api}: {tokens}")

    except Exception as e:
        logger.error(f"Example failed: {e}")


if __name__ == "__main__":
    main()