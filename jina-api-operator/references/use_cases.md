# Jina AI Use Cases and Implementation Patterns

This document provides real-world implementation patterns and workflows for Jina AI's Search Foundation platform across various applications and industries.

## Table of Contents

- [Common Implementation Patterns](#common-implementation-patterns)
- [Industry-Specific Use Cases](#industry-specific-use-cases)
- [Integration Examples](#integration-examples)
- [Best Practices](#best-practices)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Common Implementation Patterns

### 1. RAG (Retrieval-Augmented Generation) System

#### Overview
Combine document retrieval with LLM generation for accurate, context-aware responses.

#### Implementation
```python
class JinaRAGSystem:
    def __init__(self, api_key, embedding_model="jina-embeddings-v4"):
        self.client = JinaAPIClient(api_key)
        self.embedding_model = embedding_model
        self.documents = []
        self.embeddings = []
        self.reranker_model = "jina-reranker-v3"

    def add_documents_from_urls(self, urls):
        """Add documents from web URLs"""
        for url in urls:
            try:
                # Extract content
                content = self.client.read_url(url)
                text = content['content']

                # Split into chunks
                chunks = self.client.chunk_text(text, max_chunk_length=1000)

                for chunk in chunks:
                    self.documents.append({
                        'url': url,
                        'content': chunk,
                        'metadata': {
                            'title': content.get('title', ''),
                            'source': url
                        }
                    })

            except Exception as e:
                print(f"Failed to process {url}: {e}")

    def index_documents(self):
        """Generate embeddings for all documents"""
        print(f"Indexing {len(self.documents)} documents...")

        texts = [doc['content'] for doc in self.documents]
        self.embeddings = self.client.create_embeddings(texts, model=self.embedding_model)

    def search(self, query, top_k=5, use_reranker=True):
        """Search documents with optional reranking"""
        # Generate query embedding
        query_embedding = self.client.create_embeddings([query], model=self.embedding_model)[0]

        # Initial similarity search
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        candidates = [self.documents[i] for i in top_indices]

        if use_reranker:
            # Rerank for better results
            reranked = self.client.rerank_documents(
                query,
                [doc['content'] for doc in candidates],
                model=self.reranker_model,
                top_n=top_k
            )

            # Map reranked results back to documents
            results = []
            for result in reranked:
                doc = candidates[result['index']]
                doc['relevance_score'] = result['relevance_score']
                results.append(doc)

            return results

        return candidates

    def generate_response(self, query, context_docs, llm_client):
        """Generate response using retrieved context"""
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['content']}"
            for i, doc in enumerate(context_docs)
        ])

        prompt = f"""Based on the following context, answer the question: {query}

Context:
{context}

Answer:"""

        # Use your preferred LLM here
        response = llm_client.generate(prompt)
        return response
```

#### Usage Examples
```python
# Initialize RAG system
rag = JinaRAGSystem(api_key="your-key")

# Add documentation
docs = [
    "https://docs.python.org/3/tutorial/",
    "https://jina.ai/docs/",
    "https://example.com/technical-guide"
]
rag.add_documents_from_urls(docs)
rag.index_documents()

# Search and generate
results = rag.search("How to implement web scraping with Python?", top_k=3)
response = rag.generate_response("How to implement web scraping with Python?", results, llm_client)
```

### 2. Content Classification Pipeline

#### Overview
Automatically categorize and route content based on type, sentiment, or custom criteria.

#### Implementation
```python
class ContentClassifier:
    def __init__(self, api_key):
        self.client = JinaAPIClient(api_key)

        # Predefined categories
        self.categories = {
            'content_type': ['article', 'blog', 'documentation', 'forum', 'news'],
            'sentiment': ['positive', 'negative', 'neutral'],
            'technical_level': ['beginner', 'intermediate', 'advanced'],
            'domain': ['technology', 'business', 'science', 'arts']
        }

    def train_custom_classifier(self, training_data, category_name):
        """Train a classifier for custom categories"""
        formatted_data = []
        for item in training_data:
            formatted_data.append({
                'text': item['text'],
                'label': item['label']
            })

        classifier_id = self.client.train_classifier(
            formatted_data,
            num_iters=5
        )

        return classifier_id

    def classify_content(self, text, classifier_id=None):
        """Classify content using zero-shot or trained classifier"""
        if classifier_id:
            # Use trained classifier
            result = self.client.classify_with_trained(
                classifier_id,
                [{"text": text}]
            )
            return result[0]
        else:
            # Zero-shot classification
            results = []
            for category, labels in self.categories.items():
                result = self.client.classify_zero_shot(
                    [{"text": text}],
                    labels
                )

                # Get best match
                best_result = max(result, key=lambda x: x['confidence'])
                results.append({
                    'category': category,
                    'label': best_result['label'],
                    'confidence': best_result['confidence']
                })

            return results

    def batch_classify(self, texts, classifier_ids=None):
        """Classify multiple texts efficiently"""
        results = []

        for text in texts:
            classification = self.classify_content(text, classifier_ids)
            results.append({
                'text': text[:100] + '...' if len(text) > 100 else text,
                'classification': classification
            })

        return results
```

### 3. Document Processing Pipeline

#### Overview
Extract, process, and analyze documents from various sources.

#### Implementation
```python
class DocumentProcessor:
    def __init__(self, api_key):
        self.client = JinaAPIClient(api_key)
        self.processed_docs = []

    def process_document(self, source, doc_type='url'):
        """Process document from URL or file"""
        if doc_type == 'url':
            return self._process_url(source)
        elif doc_type == 'file':
            return self._process_file(source)
        else:
            raise ValueError(f"Unsupported doc_type: {doc_type}")

    def _process_url(self, url):
        """Process document from URL"""
        try:
            # Extract content
            content = self.client.read_url(url)
            text = content['content']
            title = content.get('title', '')

            # Analyze content
            analysis = self._analyze_content(text)

            # Segment into sections
            segments = self._segment_document(text)

            processed = {
                'source': url,
                'title': title,
                'content': text,
                'analysis': analysis,
                'segments': segments,
                'metadata': {
                    'word_count': len(text.split()),
                    'char_count': len(text),
                    'processed_at': time.time()
                }
            }

            self.processed_docs.append(processed)
            return processed

        except Exception as e:
            return {'error': str(e), 'source': url}

    def _analyze_content(self, text):
        """Analyze document content"""
        # Sentiment analysis
        sentiment_result = self.client.classify_zero_shot(
            [{"text": text[:1000]}],  # Limit text length
            ["positive", "negative", "neutral"]
        )

        # Content type classification
        content_result = self.client.classify_zero_shot(
            [{"text": text[:500]}],
            ["technical", "business", "news", "educational", "marketing"]
        )

        # Extract key topics using embeddings (simplified)
        key_phrases = self._extract_key_phrases(text)

        return {
            'sentiment': sentiment_result[0],
            'content_type': content_result[0],
            'key_phrases': key_phrases,
            'readability_score': self._calculate_readability(text)
        }

    def _segment_document(self, text):
        """Segment document into logical sections"""
        chunks = self.client.chunk_text(text, max_chunk_length=800)

        segments = []
        for i, chunk in enumerate(chunks):
            # Classify segment type
            segment_type = self._classify_segment_type(chunk)

            segments.append({
                'id': i,
                'content': chunk,
                'type': segment_type,
                'word_count': len(chunk.split())
            })

        return segments

    def _classify_segment_type(self, segment):
        """Classify the type of document segment"""
        # Look for headers, lists, code blocks, etc.
        if segment.strip().startswith('#'):
            return 'heading'
        elif any(marker in segment for marker in ['*', '-', '1.', '2.']):
            return 'list'
        elif '```' in segment:
            return 'code'
        elif len(segment.split()) < 10:
            return 'short'
        else:
            return 'paragraph'

    def _extract_key_phrases(self, text, max_phrases=10):
        """Extract key phrases using simple heuristics"""
        # This is a simplified implementation
        words = text.lower().split()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}

        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Get top phrases
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:max_phrases]
        return [word for word, _ in top_words]

    def _calculate_readability(self, text):
        """Simple readability score calculation"""
        sentences = text.split('.')
        if not sentences:
            return 0

        words = text.split()
        avg_sentence_length = len(words) / len(sentences)

        # Simplified Flesch Reading Ease approximation
        readability_score = 100 - (avg_sentence_length * 2)
        return max(0, min(100, readability_score))

    def batch_process(self, sources, doc_type='url'):
        """Process multiple documents"""
        results = []

        for source in sources:
            result = self.process_document(source, doc_type)
            results.append(result)

            # Rate limiting
            time.sleep(0.1)

        return results
```

---

## Industry-Specific Use Cases

### 1. E-commerce Product Catalog

#### Use Case: Product Search and Recommendation
```python
class ECommerceSearch:
    def __init__(self, api_key):
        self.client = JinaAPIClient(api_key)
        self.products = []
        self.embeddings = []

    def index_products(self, products):
        """Index product catalog"""
        for product in products:
            # Create searchable text
            searchable_text = f"{product['name']} {product['description']} {' '.join(product.get('tags', []))}"

            self.products.append({
                'id': product['id'],
                'name': product['name'],
                'text': searchable_text,
                'price': product.get('price'),
                'category': product.get('category'),
                'metadata': product
            })

        # Generate embeddings
        texts = [p['text'] for p in self.products]
        self.embeddings = self.client.create_embeddings(texts)

    def search_products(self, query, category_filter=None, price_range=None):
        """Search products with filters"""
        query_embedding = self.client.create_embeddings([query])[0]
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]

        # Get top results
        top_indices = np.argsort(similarities)[-20:][::-1]
        candidates = [self.products[i] for i in top_indices]

        # Apply filters
        filtered_results = []
        for product in candidates:
            if category_filter and product.get('category') != category_filter:
                continue
            if price_range and not (price_range[0] <= product.get('price', 0) <= price_range[1]):
                continue
            filtered_results.append(product)

        return filtered_results[:10]

    def recommend_similar(self, product_id, top_k=5):
        """Find similar products"""
        target_product = next((p for p in self.products if p['id'] == product_id), None)
        if not target_product:
            return []

        target_embedding = self.embeddings[self.products.index(target_product)]
        similarities = cosine_similarity([target_embedding], self.embeddings)[0]

        # Get similar products (exclude self)
        similar_indices = np.argsort(similarities)[-top_k-1:][::-1]
        similar_products = [self.products[i] for i in similar_indices if self.products[i]['id'] != product_id]

        return similar_products
```

### 2. Financial Document Analysis

#### Use Case: Financial Report Processing
```python
class FinancialAnalyzer:
    def __init__(self, api_key):
        self.client = JinaAPIClient(api_key)
        self.financial_classifier_id = None
        self._train_financial_classifier()

    def _train_financial_classifier(self):
        """Train classifier for financial documents"""
        training_data = [
            {"text": "Revenue increased by 15% year-over-year", "label": "positive"},
            {"text": "Net loss of $2.3 million due to market conditions", "label": "negative"},
            {"text": "Operating expenses remained stable at $500k", "label": "neutral"},
            # ... more training data
        ]

        self.financial_classifier_id = self.client.train_classifier(training_data, num_iters=10)

    def analyze_financial_report(self, report_text):
        """Analyze financial report"""
        # Sentiment analysis
        sentiment = self.client.classify_with_trained(
            self.financial_classifier_id,
            [{"text": report_text[:1000]}]  # Limit length
        )

        # Extract financial metrics
        metrics = self._extract_financial_metrics(report_text)

        # Risk assessment
        risk_score = self._assess_risk(report_text)

        return {
            'sentiment': sentiment[0],
            'metrics': metrics,
            'risk_score': risk_score,
            'summary': self._generate_summary(report_text, sentiment, metrics)
        }

    def _extract_financial_metrics(self, text):
        """Extract financial metrics from text"""
        # This would use regex patterns or NER in production
        metrics = {
            'revenue_mentions': len(re.findall(r'\$[\d,]+\.?\d*\s*(?:million|billion|thousand)', text, re.IGNORECASE)),
            'percentage_changes': len(re.findall(r'\d+\.?\d*%', text)),
            'financial_terms': len(re.findall(r'(?:revenue|profit|loss|expense|income|cost)', text, re.IGNORECASE))
        }
        return metrics

    def _assess_risk(self, text):
        """Assess financial risk level"""
        risk_keywords = ['loss', 'decline', 'risk', 'uncertainty', 'debt']
        risk_score = sum(1 for keyword in risk_keywords if keyword in text.lower())
        return min(10, risk_score)  # Cap at 10

    def _generate_summary(self, text, sentiment, metrics):
        """Generate executive summary"""
        summary_points = []

        if sentiment['label'] == 'positive':
            summary_points.append("Financial performance shows positive indicators")
        elif sentiment['label'] == 'negative':
            summary_points.append("Financial performance shows concerning trends")

        if metrics['percentage_changes'] > 0:
            summary_points.append(f"Document contains {metrics['percentage_changes']} percentage changes")

        return summary_points
```

### 3. Academic Research Assistant

#### Use Case: Literature Review and Analysis
```python
class ResearchAssistant:
    def __init__(self, api_key):
        self.client = JinaAPIClient(api_key)
        self.paper_database = []
        self.embeddings = []

    def add_papers_from_urls(self, urls):
        """Add academic papers from URLs"""
        for url in urls:
            if 'arxiv.org' in url:
                paper = self._process_arxiv_paper(url)
            else:
                paper = self._process_general_paper(url)

            if paper:
                self.paper_database.append(paper)

    def _process_arxiv_paper(self, url):
        """Process arXiv paper specifically"""
        try:
            content = self.client.read_url(url)
            text = content['content']

            # Extract arXiv metadata
            arxiv_id = url.split('/')[-1]
            title = content.get('title', '')

            return {
                'id': arxiv_id,
                'title': title,
                'url': url,
                'content': text,
                'type': 'academic',
                'source': 'arxiv'
            }
        except Exception as e:
            print(f"Failed to process arXiv paper {url}: {e}")
            return None

    def _process_general_paper(self, url):
        """Process general academic paper"""
        try:
            content = self.client.read_url(url)
            return {
                'url': url,
                'title': content.get('title', ''),
                'content': content['content'],
                'type': 'academic',
                'source': 'web'
            }
        except Exception as e:
            print(f"Failed to process paper {url}: {e}")
            return None

    def index_papers(self):
        """Index papers for search"""
        texts = [paper['content'] for paper in self.paper_database]
        self.embeddings = self.client.create_embeddings(texts)

    def literature_search(self, query, max_results=10):
        """Search academic literature"""
        if not self.embeddings:
            return []

        query_embedding = self.client.create_embeddings([query])[0]
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]

        top_indices = np.argsort(similarities)[-max_results:][::-1]
        results = [self.paper_database[i] for i in top_indices]

        # Rerank for better results
        reranked = self.client.rerank_documents(
            query,
            [paper['content'][:1000] for paper in results],  # Limit content length
            top_n=max_results
        )

        # Map back to papers
        final_results = []
        for result in reranked:
            paper = results[result['index']]
            paper['relevance_score'] = result['relevance_score']
            final_results.append(paper)

        return final_results

    def comprehensive_research(self, topic):
        """Use DeepSearch for comprehensive research"""
        messages = [
            {
                "role": "user",
                "content": f"Conduct a comprehensive literature review on: {topic}. "
                           f"Include recent developments, key findings, and future directions. "
                           f"Provide citations and references to support claims."
            }
        ]

        return self.client.deepsearch(
            messages,
            reasoning_effort="high",
            budget_tokens=300000,
            arxiv_optimized=True
        )
```

---

## Integration Examples

### 1. FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class SearchRequest(BaseModel):
    query: str
    max_results: int = 10
    category: Optional[str] = None
    use_reranking: bool = True

class SearchResult(BaseModel):
    content: str
    title: str
    url: str
    relevance_score: float

# Initialize Jina client
jina_client = JinaAPIClient(api_key="your-api-key")

@app.post("/search", response_model=List[SearchResult])
async def search_documents(request: SearchRequest):
    try:
        # Implement search logic here using jina_client
        results = jina_client.search_web(request.query)

        # Convert to SearchResult format
        formatted_results = []
        for result in results[:request.max_results]:
            formatted_results.append(SearchResult(
                content=result.get('content', ''),
                title=result.get('title', ''),
                url=result.get('url', ''),
                relevance_score=1.0  # Placeholder
            ))

        return formatted_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embeddings")
async def create_embeddings(texts: List[str]):
    try:
        embeddings = jina_client.create_embeddings(texts)
        return {"embeddings": embeddings, "count": len(embeddings)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Streamlit Integration

```python
import streamlit as st
import pandas as pd

st.title("Jina AI Document Search")

# Initialize client
@st.cache_resource
def get_client():
    return JinaAPIClient(api_key=st.secrets.get("JINA_API_KEY"))

client = get_client()

# UI Components
st.header("Document Search and Analysis")

query = st.text_input("Enter your search query:")
max_results = st.slider("Max results", 1, 50, 10)

if query:
    with st.spinner("Searching documents..."):
        # Perform search
        results = client.search_web(query)

        # Display results
        st.subheader(f"Found {len(results)} results")

        for i, result in enumerate(results[:max_results]):
            with st.expander(f"Result {i+1}: {result.get('title', 'No title')}"):
                st.write(result.get('content', 'No content available'))
                st.caption(f"Source: {result.get('url', 'Unknown source')}")

# Embeddings feature
st.header("Text Embeddings")

texts_to_embed = st.text_area("Enter texts to embed (one per line):").split('\n')
texts_to_embed = [t.strip() for t in texts_to_embed if t.strip()]

if st.button("Generate Embeddings") and texts_to_embed:
    with st.spinner("Generating embeddings..."):
        embeddings = client.create_embeddings(texts_to_embed)

        st.success(f"Generated {len(embeddings)} embeddings")

        # Display first embedding dimensions
        if embeddings:
            st.write(f"Embedding dimensions: {len(embeddings[0])}")

            # Create DataFrame for visualization
            df = pd.DataFrame({
                'Text': texts_to_embed,
                'Embedding Preview': [str(emb[:5]) + '...' for emb in embeddings]
            })
            st.dataframe(df)
```

### 3. WordPress Integration

```php
<?php
// WordPress plugin for Jina AI integration

class Jina_AI_Integration {
    private $api_key;
    private $client;

    public function __construct($api_key) {
        $this->api_key = $api_key;
        $this->client = $this->initialize_client();
    }

    private function initialize_client() {
        // Initialize Python bridge or HTTP client
        return new JinaAPIClient($this->api_key);
    }

    public function search_content($query, $max_results = 10) {
        try {
            $results = $this->client->search_web($query);
            return array_slice($results, 0, $max_results);
        } catch (Exception $e) {
            error_log("Jina AI search error: " . $e->getMessage());
            return [];
        }
    }

    public function create_embeddings($texts) {
        try {
            return $this->client->create_embeddings($texts);
        } catch (Exception $e) {
            error_log("Jina AI embeddings error: " . $e->getMessage());
            return [];
        }
    }

    public function classify_content($content, $labels) {
        try {
            $results = $this->client->classify_zero_shot(
                [['text' => $content]],
                $labels
            );
            return $results[0];
        } catch (Exception $e) {
            error_log("Jina AI classification error: " . $e->getMessage());
            return null;
        }
    }
}

// WordPress integration
add_action('init', function() {
    $jina_ai = new Jina_AI_Integration(get_option('jina_api_key'));

    // Add custom REST API endpoints
    add_action('rest_api_init', function() {
        register_rest_route('/jina-ai/search', 'GET', 'jina_ai_search_handler');
        register_rest_route('/jina-ai/embeddings', 'POST', 'jina_ai_embeddings_handler');
    });
});

function jina_ai_search_handler($request) {
    $query = $request->get_param('query');
    $max_results = $request->get_param('max_results', 10);

    $jina_ai = new Jina_AI_Integration(get_option('jina_api_key'));
    $results = $jina_ai->search_content($query, $max_results);

    return new WP_REST_Response($results, 200);
}

function jina_ai_embeddings_handler($request) {
    $texts = $request->get_json_params();

    $jina_ai = new Jina_AI_Integration(get_option('jina_api_key'));
    $embeddings = $jina_ai->create_embeddings($texts);

    return new WP_REST_Response($embeddings, 200);
}
```

---

## Best Practices

### 1. Error Handling

```python
class RobustJinaClient:
    def __init__(self, api_key, max_retries=3):
        self.client = JinaAPIClient(api_key)
        self.max_retries = max_retries
        self.retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff

    def make_robust_request(self, method, *args, **kwargs):
        """Make request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                return getattr(self.client, method)(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise

                if "429" in str(e) or "timeout" in str(e).lower():
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    time.sleep(delay)
                    continue

                raise  # Re-raise non-retryable errors

    def safe_create_embeddings(self, texts):
        """Create embeddings with error handling"""
        try:
            return self.make_robust_request('create_embeddings', texts)
        except Exception as e:
            logger.error(f"Embedding creation failed: {e}")
            return None

    def safe_search(self, query):
        """Search with error handling"""
        try:
            return self.make_robust_request('search_web', query)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
```

### 2. Caching Strategy

```python
class SmartCache:
    def __init__(self, cache_dir="cache", default_ttl=3600):
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(exist_ok=True)

    def get_cache_key(self, *args, **kwargs):
        """Generate cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key, ttl=None):
        """Get cached item"""
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            cache_age = time.time() - data['timestamp']
            item_ttl = ttl or self.default_ttl

            if cache_age < item_ttl:
                return data['value']

        except (json.JSONDecodeError, IOError):
            pass

        return None

    def set(self, key, value, ttl=None):
        """Set cached item"""
        cache_file = self.cache_dir / f"{key}.json"

        data = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl or self.default_ttl
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except IOError:
            pass

# Usage
cache = SmartCache()

# Cache embeddings
cache_key = cache.get_cache_key("embeddings", texts)
embeddings = cache.get(cache_key)

if embeddings is None:
    embeddings = client.create_embeddings(texts)
    cache.set(cache_key, embeddings, ttl=7200)  # 2 hours
```

### 3. Batch Processing

```python
class BatchProcessor:
    def __init__(self, client, batch_size=50, delay=0.1):
        self.client = client
        self.batch_size = batch_size
        self.delay = delay

    def process_embeddings_batch(self, texts):
        """Process embeddings in batches"""
        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]

            try:
                batch_embeddings = self.client.create_embeddings(batch)
                all_embeddings.extend(batch_embeddings)

                # Rate limiting
                if i + self.batch_size < len(texts):
                    time.sleep(self.delay)

            except Exception as e:
                logger.error(f"Batch processing failed at {i}: {e}")
                # Add null placeholders for failed batch
                all_embeddings.extend([None] * len(batch))

        return all_embeddings

    def process_search_batch(self, queries):
        """Process multiple searches in batches"""
        results = {}

        for i, query in enumerate(queries):
            try:
                results[query] = self.client.search_web(query)

                if i < len(queries) - 1:
                    time.sleep(self.delay)

            except Exception as e:
                logger.error(f"Search failed for '{query}': {e}")
                results[query] = []

        return results
```

---

## Troubleshooting Common Issues

### 1. Rate Limit Exceeded

```python
# Symptom: 429 status code
# Solution: Implement exponential backoff

def handle_rate_limit_error():
    delay = 1  # Start with 1 second
    max_delay = 60  # Maximum 60 seconds

    while True:
        try:
            # Retry request
            return make_request()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if delay >= max_delay:
                    raise  # Max retries reached

                time.sleep(delay)
                delay = min(delay * 2, max_delay)
            else:
                raise
```

### 2. Large Document Processing

```python
# Symptom: Timeout or token limit exceeded
# Solution: Process in chunks

def process_large_document(url, max_chunk_size=1000):
    # Extract content
    content = client.read_url(url)
    text = content['content']

    # Check if chunking is needed
    if len(text) > max_chunk_size * 10:  # Arbitrary threshold
        # Process in chunks
        chunks = client.chunk_text(text, max_chunk_length=max_chunk_size)

        for chunk in chunks:
            process_chunk(chunk)

    else:
        # Process whole document
        process_document(text)
```

### 3. Authentication Issues

```python
# Symptom: 401 Unauthorized error
# Solution: Verify API key

def validate_api_key(api_key):
    # Test API key with simple request
    test_client = JinaAPIClient(api_key)

    try:
        result = test_client.tokenize_text("test")
        return True
    except Exception:
        return False

# Usage
if not validate_api_key(api_key):
    raise ValueError("Invalid API key")
```

### 4. Memory Issues with Large Embeddings

```python
# Symptom: Memory usage too high
# Solution: Process in smaller batches

def memory_efficient_embeddings(texts, batch_size=100):
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]

        # Process batch
        embeddings = client.create_embeddings(batch)
        all_embeddings.extend(embeddings)

        # Clear memory if needed
        if i % (batch_size * 10) == 0:
            import gc
            gc.collect()  # Force garbage collection

    return all_embeddings
```

### 5. Network Connectivity Issues

```python
# Symptom: Connection timeout or network errors
# Solution: Implement timeout and retry logic

def robust_request_with_timeout(url, timeout=30, max_retries=3):
    session = requests.Session()

    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                raise TimeoutError(f"Request timed out after {max_retries} attempts")

            wait_time = (2 ** attempt) * 5  # Exponential backoff
            time.sleep(wait_time)

        except requests.exceptions.ConnectionError:
            if attempt == max_retries - 1:
                raise ConnectionError("Failed to connect after multiple attempts")

            time.sleep(5)  # Wait before retrying
```

This comprehensive guide should help you implement Jina AI effectively across various use cases while avoiding common pitfalls and optimizing for performance and cost.