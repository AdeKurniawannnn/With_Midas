# Jina AI Rate Limits and Optimization Guide

This document provides comprehensive information about rate limits, cost optimization, and performance tuning for all Jina AI APIs.

## Table of Contents

- [Overview](#overview)
- [Rate Limits by API](#rate-limits-by-api)
- [Understanding Rate Limits](#understanding-rate-limits)
- [Cost Optimization Strategies](#cost-optimization-strategies)
- [Performance Tuning](#performance-tuning)
- [Rate Limit Handling](#rate-limit-handling)
- [Budget Management](#budget-management)
- [Monitoring and Analytics](#monitoring-and-analytics)

---

## Overview

Jina AI uses a token-based pricing model with rate limits measured in:

- **RPM**: Requests Per Minute
- **TPM**: Tokens Per Minute

Rate limits are enforced per IP address (no API key) or per API key (with authentication).

## Rate Limits by API

### Reader API

| Tier | Endpoint | RPM | TPM | Avg Latency | Token Counting |
|------|----------|-----|-----|-------------|----------------|
| No Key | `r.jina.ai` | 20 | N/A | 7.9s | Output tokens |
| Standard | `r.jina.ai` | 500 | N/A | 7.9s | Output tokens |
| Premium | `r.jina.ai` | 5000 | N/A | 7.9s | Output tokens |
| No Key | `s.jina.ai` | Blocked | N/A | - | Fixed 10K min |
| Standard | `s.jina.ai` | 100 | N/A | 2.5s | Fixed 10K min |
| Premium | `s.jina.ai` | 1000 | N/A | 2.5s | Fixed 10K min |

### Embeddings API

| Tier | RPM | TPM | Avg Latency | Token Counting |
|------|-----|-----|-------------|----------------|
| No Key | Blocked | Blocked | - | - |
| Standard | 500 | 1,000,000 | Variable | Input tokens |
| Premium | 2000 | 5,000,000 | Variable | Input tokens |

### Reranker API

| Tier | RPM | TPM | Avg Latency | Token Counting |
|------|-----|-----|-------------|----------------|
| No Key | Blocked | Blocked | - | - |
| Standard | 500 | 1,000,000 | Variable | Input tokens |
| Premium | 2000 | 5,000,000 | Variable | Input tokens |

### Classifier API

#### Zero-Shot Classification

| Tier | RPM | TPM | Avg Latency | Token Counting |
|------|-----|-----|-------------|----------------|
| No Key | Blocked | Blocked | - | - |
| Standard | 200 | 500,000 | Variable | Input + Label tokens |
| Premium | 1000 | 3,000,000 | Variable | Input + Label tokens |

#### Few-Shot Classification

| Tier | RPM | TPM | Avg Latency | Token Counting |
|------|-----|-----|-------------|----------------|
| No Key | Blocked | Blocked | - | - |
| Standard | 20 | 200,000 | Variable | Input tokens |
| Premium | 60 | 1,000,000 | Variable | Input tokens |

#### Training

| Tier | RPM | TPM | Avg Latency | Token Counting |
|------|-----|-----|-------------|----------------|
| No Key | Blocked | Blocked | Variable | Input × Iterations |
| Standard | 20 | 200,000 | Variable | Input × Iterations |
| Premium | 60 | 1,000,000 | Variable | Input × Iterations |

### Segmenter API

| Tier | RPM | TPM | Avg Latency | Token Counting |
|------|-----|-----|-------------|----------------|
| No Key | 20 | N/A | 0.3s | FREE |
| Standard | 200 | N/A | 0.3s | FREE |
| Premium | 1000 | N/A | 0.3s | FREE |

### DeepSearch API

| Tier | RPM | TPM | Avg Latency | Token Counting |
|------|-----|-----|-------------|----------------|
| No Key | Blocked | Blocked | - | - |
| Standard | 50 | N/A | 56.7s | Total process tokens |
| Premium | 500 | N/A | 56.7s | Total process tokens |

---

## Understanding Rate Limits

### How Rate Limits Work

1. **Dual Tracking**: Both RPM and TPM are tracked simultaneously
2. **First Trigger**: Limit is triggered when either RPM or TPM threshold is reached
3. **Key vs IP**: With API key, limits are tracked by key; without key, by IP address
4. **Reset**: Limits reset on a per-minute basis

### Rate Limit Headers

API responses include rate limit information:

```http
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 499
X-RateLimit-Reset: 1642652800
```

### Common Rate Limit Scenarios

#### Scenario 1: High Volume Text Processing
```
Embeddings API: 500 RPM, 1M TPM
- Can send 500 requests per minute
- Or 1M tokens per minute
- Or combination (e.g., 250 requests with 2K tokens each = 500K tokens)
```

#### Scenario 2: Mixed API Usage
```
- Reader: 500 RPM
- Embeddings: 500 RPM, 1M TPM
- Reranker: 500 RPM, 1M TPM
Total: 1500 RPM across all APIs
```

---

## Cost Optimization Strategies

### Token Usage Patterns

#### Reader API
- **URL Reading**: ~1 token per character of output
- **Web Search**: Fixed 10,000 tokens minimum
- **Images**: Add ~100-500 tokens each
- **Links/Sections**: Add ~50-200 tokens each

#### Embeddings API
- **Text**: ~1 token per 4 characters of input
- **Images**: Variable based on size and model
  - jina-embeddings-v4: 10 tokens per 28x28 tile
  - jina-clip-v2: 4000 tokens per 512x512 tile
  - jina-clip-v1: 1000 tokens per 224x224 tile

#### Reranker API
- **Text**: ~1 token per 4 characters (query + documents)

#### DeepSearch API
- **Average**: ~70,000 tokens per query
- **Range**: 10,000 - 500,000 tokens
- **Variables**: Query complexity, reasoning effort, team size

### Optimization Techniques

#### 1. Batch Processing

```python
# Instead of individual requests
for text in texts:
    embedding = client.create_embeddings([text])

# Use batch processing
batch_size = 100
for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    embeddings = client.create_embeddings(batch)
```

#### 2. Smart Caching

```python
# Cache embeddings for repeated content
cache = {}

def get_embedding(text, cache_ttl=3600):
    cache_key = hashlib.md5(text.encode()).hexdigest()

    if cache_key in cache:
        cached_time, result = cache[cache_key]
        if time.time() - cached_time < cache_ttl:
            return result

    result = client.create_embeddings([text])[0]
    cache[cache_key] = (time.time(), result)
    return result
```

#### 3. Content Preprocessing

```python
# Remove unnecessary content before Reader API
def clean_url_content(url):
    # Skip known low-value pages
    skip_patterns = ['/privacy', '/terms', '/ads']
    if any(pattern in url for pattern in skip_patterns):
        return None

    # Remove query parameters for caching
    url = url.split('?')[0]
    return url
```

#### 4. Model Selection

```python
# Choose optimal model for task
def choose_embedding_model(task_type, content_type):
    if content_type == 'code':
        return 'jina-code-embeddings-1.5b'
    elif content_type == 'image':
        return 'jina-embeddings-v4'
    elif task_type == 'search':
        return 'jina-embeddings-v3'
    else:
        return 'jina-embeddings-v4'
```

#### 5. Token Budget Management

```python
class TokenBudget:
    def __init__(self, daily_limit=100000):
        self.daily_limit = daily_limit
        self.used_today = 0
        self.last_reset = time.time()

    def can_spend(self, tokens):
        self._check_daily_reset()
        return (self.used_today + tokens) <= self.daily_limit

    def spend(self, tokens):
        self.used_today += tokens

    def _check_daily_reset(self):
        if time.time() - self.last_reset > 86400:  # 24 hours
            self.used_today = 0
            self.last_reset = time.time()
```

---

## Performance Tuning

### Request Optimization

#### 1. Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter

session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3
)
session.mount('https://', adapter)
```

#### 2. Timeout Management

```python
# Different timeouts for different APIs
timeouts = {
    'reader': 30,      # Web scraping can be slow
    'embeddings': 10,   # Usually fast
    'reranker': 5,      # Quick processing
    'deepsearch': 120,  # Long-running process
    'classifier': 10
}
```

#### 3. Async Processing

```python
import aiohttp
import asyncio

async def batch_embeddings(texts, batch_size=50):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            task = create_embeddings_async(session, batch)
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]
```

### Model-Specific Optimizations

#### Reader API

```python
# Optimize Reader requests
reader_params = {
    'browser_engine': 'default',  # Balance speed/quality
    'timeout': 15,               # Don't wait too long
    'remove_images': 'true',      # Save tokens if images not needed
    'json_response': 'true'       # Faster parsing
}
```

#### Embeddings API

```python
# Optimize embedding dimensions
def optimize_dimensions(purpose):
    if purpose == 'search':
        return 512   # Good for search, saves space
    elif purpose == 'retrieval':
        return 1024  # Balanced
    else:
        return 2048  # Highest quality
```

#### DeepSearch API

```python
# Optimize DeepSearch parameters
deepsearch_params = {
    'reasoning_effort': 'medium',  # Balance quality/cost
    'team_size': 1,               # Start small, increase if needed
    'budget_tokens': 200000,       # Reasonable limit
    'max_attempts': 3              # Prevent endless loops
}
```

---

## Rate Limit Handling

### Exponential Backoff

```python
import time
import random

def make_request_with_backoff(url, headers, data, max_retries=5):
    base_delay = 1
    max_delay = 60

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                # Calculate delay with jitter
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                time.sleep(delay)
                continue
            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            time.sleep(delay)
```

### Adaptive Rate Limiting

```python
class AdaptiveRateLimiter:
    def __init__(self, initial_rpm=10):
        self.current_rpm = initial_rpm
        self.requests = []
        self.last_adjustment = time.time()

    def wait_if_needed(self):
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]

        if len(self.requests) >= self.current_rpm:
            sleep_time = 60 - (now - self.requests[0])
            time.sleep(sleep_time)

        self.requests.append(now)

    def adjust_rate(self, success_rate):
        now = time.time()
        if now - self.last_adjustment < 300:  # Adjust every 5 minutes
            return

        if success_rate > 0.95:  # High success rate, increase
            self.current_rpm = min(self.current_rpm * 1.2, 1000)
        elif success_rate < 0.8:  # Low success rate, decrease
            self.current_rpm = max(self.current_rpm * 0.8, 1)

        self.last_adjustment = now
```

### Queue-Based Processing

```python
import queue
import threading
import time

class APIQueue:
    def __init__(self, max_workers=5):
        self.queue = queue.Queue()
        self.workers = []
        self.max_workers = max_workers
        self.start_workers()

    def start_workers(self):
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def _worker(self):
        while True:
            try:
                task = self.queue.get(timeout=1)
                if task is None:  # Shutdown signal
                    break

                func, args, kwargs = task
                result = func(*args, **kwargs)

                # Store result or handle callback
                self.queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")

    def add_task(self, func, *args, **kwargs):
        self.queue.put((func, args, kwargs))

    def wait_completion(self):
        self.queue.join()
```

---

## Budget Management

### Token Cost Estimation

```python
class CostEstimator:
    # Pricing (tokens per USD approximately)
    PRICING = {
        'standard': 0.05 / 1_000_000,  # $50 per 1B tokens
        'premium': 0.045 / 1_000_000   # $45 per 1B tokens
    }

    def __init__(self, tier='standard'):
        self.tier = tier
        self.cost_per_token = self.PRICING[tier]

    def estimate_cost(self, token_counts):
        total_tokens = sum(token_counts.values())
        return total_tokens * self.cost_per_token

    def estimate_reader_cost(self, content_length):
        tokens = content_length  # Rough estimate
        return tokens * self.cost_per_token

    def estimate_search_cost(self):
        return 10000 * self.cost_per_token  # Minimum 10K tokens

    def estimate_embeddings_cost(self, input_length):
        tokens = input_length // 4
        return tokens * self.cost_per_token

    def estimate_deepsearch_cost(self):
        return 70000 * self.cost_per_token  # Average cost
```

### Budget Tracking

```python
class BudgetTracker:
    def __init__(self, monthly_budget_usd=100):
        self.monthly_budget = monthly_budget_usd
        self.cost_estimator = CostEstimator()
        self.spent_this_month = 0
        self.usage_log = []

    def track_usage(self, api_name, token_count):
        cost = self.cost_estimator.estimate_cost({api_name: token_count})
        self.spent_this_month += cost

        self.usage_log.append({
            'timestamp': time.time(),
            'api': api_name,
            'tokens': token_count,
            'cost': cost,
            'monthly_total': self.spent_this_month
        })

    def can_afford(self, estimated_tokens):
        estimated_cost = estimated_tokens * self.cost_estimator.cost_per_token
        remaining_budget = self.monthly_budget - self.spent_this_month
        return estimated_cost <= remaining_budget

    def get_usage_report(self):
        return {
            'monthly_budget': self.monthly_budget,
            'spent': self.spent_this_month,
            'remaining': self.monthly_budget - self.spent_this_month,
            'usage_breakdown': self._get_breakdown()
        }

    def _get_breakdown(self):
        breakdown = {}
        for entry in self.usage_log:
            api = entry['api']
            if api not in breakdown:
                breakdown[api] = {'tokens': 0, 'cost': 0}
            breakdown[api]['tokens'] += entry['tokens']
            breakdown[api]['cost'] += entry['cost']
        return breakdown
```

---

## Monitoring and Analytics

### Usage Monitoring

```python
class UsageMonitor:
    def __init__(self):
        self.metrics = {
            'requests_per_minute': [],
            'tokens_per_minute': [],
            'error_rates': [],
            'response_times': []
        }
        self.start_time = time.time()

    def record_request(self, api_name, success, response_time, tokens=0):
        now = time.time()

        # Track requests per minute
        self._track_rpm(api_name, now)

        # Track tokens per minute
        self._track_tpm(api_name, tokens, now)

        # Track response times
        self.metrics['response_times'].append({
            'timestamp': now,
            'api': api_name,
            'time': response_time
        })

        # Track errors
        if not success:
            self.metrics['error_rates'].append({
                'timestamp': now,
                'api': api_name
            })

    def _track_rpm(self, api_name, timestamp):
        # Implementation for tracking requests per minute
        pass

    def _track_tpm(self, api_name, tokens, timestamp):
        # Implementation for tracking tokens per minute
        pass

    def get_health_status(self):
        # Calculate recent metrics
        recent_time = time.time() - 300  # Last 5 minutes

        recent_errors = len([e for e in self.metrics['error_rates']
                              if e['timestamp'] > recent_time])

        avg_response_time = self._calculate_avg_response_time(recent_time)

        return {
            'error_rate_5min': recent_errors,
            'avg_response_time': avg_response_time,
            'uptime_percentage': self._calculate_uptime(),
            'status': 'healthy' if recent_errors < 5 else 'degraded'
        }
```

### Alerting System

```python
class AlertManager:
    def __init__(self, budget_threshold=0.9, error_threshold=0.1):
        self.budget_threshold = budget_threshold
        self.error_threshold = error_threshold
        self.alerts_sent = []

    def check_budget_alert(self, current_spending, monthly_budget):
        usage_ratio = current_spending / monthly_budget

        if usage_ratio >= self.budget_threshold:
            alert_key = f"budget_{int(usage_ratio * 100)}"
            if alert_key not in self.alerts_sent:
                self.send_alert(
                    "Budget Alert",
                    f"Spent {usage_ratio:.1%} of monthly budget"
                )
                self.alerts_sent.append(alert_key)

    def check_error_alert(self, error_rate):
        if error_rate >= self.error_threshold:
            alert_key = f"errors_{int(error_rate * 100)}"
            if alert_key not in self.alerts_sent:
                self.send_alert(
                    "High Error Rate",
                    f"Error rate is {error_rate:.1%}"
                )
                self.alerts_sent.append(alert_key)

    def send_alert(self, title, message):
        # Implementation for sending alerts (email, Slack, etc.)
        print(f"ALERT: {title} - {message}")
```

### Performance Analytics

```python
class PerformanceAnalyzer:
    def __init__(self):
        self.request_log = []

    def log_request(self, api_name, success, response_time, tokens, cost):
        self.request_log.append({
            'timestamp': time.time(),
            'api': api_name,
            'success': success,
            'response_time': response_time,
            'tokens': tokens,
            'cost': cost
        })

    def analyze_performance(self, time_window=3600):
        """Analyze performance over time window (default: 1 hour)"""
        cutoff_time = time.time() - time_window
        recent_requests = [
            req for req in self.request_log
            if req['timestamp'] > cutoff_time
        ]

        if not recent_requests:
            return {}

        return {
            'total_requests': len(recent_requests),
            'success_rate': sum(1 for r in recent_requests if r['success']) / len(recent_requests),
            'avg_response_time': sum(r['response_time'] for r in recent_requests) / len(recent_requests),
            'total_tokens': sum(r['tokens'] for r in recent_requests),
            'total_cost': sum(r['cost'] for r in recent_requests),
            'requests_per_minute': len(recent_requests) / (time_window / 60),
            'tokens_per_minute': sum(r['tokens'] for r in recent_requests) / (time_window / 60),
            'cost_per_minute': sum(r['cost'] for r in recent_requests) / (time_window / 60),
            'api_breakdown': self._get_api_breakdown(recent_requests)
        }

    def _get_api_breakdown(self, requests):
        breakdown = {}
        for req in requests:
            api = req['api']
            if api not in breakdown:
                breakdown[api] = {
                    'count': 0,
                    'total_time': 0,
                    'total_tokens': 0,
                    'total_cost': 0,
                    'successes': 0
                }

            breakdown[api]['count'] += 1
            breakdown[api]['total_time'] += req['response_time']
            breakdown[api]['total_tokens'] += req['tokens']
            breakdown[api]['total_cost'] += req['cost']
            if req['success']:
                breakdown[api]['successes'] += 1

        # Calculate averages
        for api in breakdown:
            count = breakdown[api]['count']
            breakdown[api]['avg_response_time'] = breakdown[api]['total_time'] / count
            breakdown[api]['success_rate'] = breakdown[api]['successes'] / count
            breakdown[api]['avg_tokens'] = breakdown[api]['total_tokens'] / count
            breakdown[api]['avg_cost'] = breakdown[api]['total_cost'] / count

        return breakdown
```

This comprehensive guide should help you optimize your Jina AI API usage, manage costs effectively, and maintain high performance across all applications.