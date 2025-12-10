#!/usr/bin/env python3
"""
Test script for Jina API Operator
Tests all 6 core APIs to verify configuration and functionality
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from jina_client import JinaAPIClient
import json

def test_reader_api(client):
    """Test Reader API - URL to markdown conversion"""
    print("\n" + "="*60)
    print("TEST 1: Reader API (URL Content Extraction)")
    print("="*60)

    try:
        url = "https://example.com"
        print(f"📖 Reading URL: {url}")

        result = client.read_url(url)

        content = result.get('content', '')
        title = result.get('title', 'N/A')

        print(f"✅ Success!")
        print(f"   Title: {title}")
        print(f"   Content length: {len(content)} characters")
        print(f"   Preview: {content[:200]}...")

        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_search_api(client):
    """Test Reader Search API - Web search and convert results"""
    print("\n" + "="*60)
    print("TEST 2: Reader Search API (Web Search)")
    print("="*60)

    try:
        query = "machine learning tutorials"
        print(f"🔍 Searching for: '{query}'")

        result = client.search_web(query)

        # Parse results
        content = result.get('content', '')

        print(f"✅ Success!")
        print(f"   Results length: {len(content)} characters")
        print(f"   Preview: {content[:300]}...")
        print(f"   Token cost: ~10,000 tokens (fixed)")

        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_embeddings_api(client):
    """Test Embeddings API - Text embeddings"""
    print("\n" + "="*60)
    print("TEST 3: Embeddings API (Text Vectors)")
    print("="*60)

    try:
        texts = [
            "Machine learning is fascinating",
            "Deep learning with neural networks",
            "Python programming basics"
        ]

        print(f"🧮 Creating embeddings for {len(texts)} texts")
        for i, text in enumerate(texts, 1):
            print(f"   {i}. {text}")

        embeddings = client.create_embeddings(texts)

        print(f"✅ Success!")
        print(f"   Generated {len(embeddings)} embeddings")
        print(f"   Dimension: {len(embeddings[0])}")
        print(f"   First embedding (first 5 values): {embeddings[0][:5]}")

        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_reranker_api(client):
    """Test Reranker API - Document reranking"""
    print("\n" + "="*60)
    print("TEST 4: Reranker API (Document Ranking)")
    print("="*60)

    try:
        query = "machine learning tutorials"
        documents = [
            "Introduction to machine learning algorithms",
            "Deep learning with neural networks",
            "Python programming basics",
            "Statistical methods for data analysis",
            "Computer vision applications"
        ]

        print(f"🔄 Reranking {len(documents)} documents")
        print(f"   Query: '{query}'")
        print(f"   Documents:")
        for i, doc in enumerate(documents, 1):
            print(f"      {i}. {doc}")

        results = client.rerank_documents(query, documents, top_n=3)

        print(f"✅ Success!")
        print(f"   Top 3 results:")
        for i, result in enumerate(results, 1):
            score = result.get('relevance_score', 'N/A')
            index = result.get('index', 'N/A')
            text = documents[index] if isinstance(index, int) else 'N/A'
            print(f"      {i}. Score: {score:.4f} - {text}")

        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_classifier_api(client):
    """Test Classifier API - Zero-shot classification"""
    print("\n" + "="*60)
    print("TEST 5: Classifier API (Zero-shot Classification)")
    print("="*60)

    try:
        inputs = [
            {"text": "I absolutely love this product!"},
            {"text": "This is terrible and broken."},
            {"text": "It's okay, nothing special."}
        ]
        labels = ["positive", "negative", "neutral"]

        print(f"🏷️  Classifying {len(inputs)} texts")
        for i, inp in enumerate(inputs, 1):
            print(f"   {i}. {inp['text']}")
        print(f"   Labels: {', '.join(labels)}")

        results = client.classify_zero_shot(inputs, labels)

        print(f"✅ Success!")
        print(f"   Results:")
        for i, result in enumerate(results, 1):
            text = result.get('text', 'N/A')
            label = result.get('label', 'N/A')
            confidence = result.get('confidence', 0)
            print(f"      {i}. '{text}' → {label} ({confidence:.2%})")

        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_segmenter_api(client):
    """Test Segmenter API - Text chunking"""
    print("\n" + "="*60)
    print("TEST 6: Segmenter API (Text Chunking)")
    print("="*60)

    try:
        long_text = """
        Machine learning is a subset of artificial intelligence that focuses on the development
        of algorithms and statistical models that enable computers to improve their performance
        on tasks through experience. Deep learning, a subfield of machine learning, uses
        artificial neural networks with multiple layers to model and understand complex patterns
        in large datasets. Neural networks are inspired by the structure and function of biological
        neural networks in animal brains. They consist of interconnected nodes (neurons) organized
        in layers, with connections having associated weights that are adjusted during training.
        """ * 3

        print(f"✂️  Chunking text ({len(long_text)} characters)")

        chunks = client.chunk_text(long_text, max_chunk_length=200)

        print(f"✅ Success!")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Chunks:")
        for i, chunk in enumerate(chunks[:3], 1):
            preview = chunk[:100].replace('\n', ' ').strip()
            print(f"      {i}. ({len(chunk)} chars) {preview}...")
        if len(chunks) > 3:
            print(f"      ... and {len(chunks) - 3} more chunks")

        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_token_tracking(client):
    """Test token usage tracking"""
    print("\n" + "="*60)
    print("TOKEN USAGE SUMMARY")
    print("="*60)

    usage = client.get_token_usage()
    total = sum(usage.values())

    print(f"\n📊 Token Usage by API:")
    for api, tokens in usage.items():
        if tokens > 0:
            print(f"   {api.capitalize():15} {tokens:,} tokens")

    print(f"\n   {'TOTAL':15} {total:,} tokens")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 JINA API OPERATOR - COMPREHENSIVE TEST SUITE")
    print("="*60)

    try:
        # Initialize client
        print("\n🔐 Initializing Jina API Client...")
        client = JinaAPIClient()
        print("✅ Client initialized successfully")

    except ValueError as e:
        print(f"❌ Initialization failed: {e}")
        return False

    # Run tests
    tests = [
        ("Reader API", test_reader_api),
        ("Search API", test_search_api),
        ("Embeddings API", test_embeddings_api),
        ("Reranker API", test_reranker_api),
        ("Classifier API", test_classifier_api),
        ("Segmenter API", test_segmenter_api),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func(client)
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results[name] = False

    # Token tracking
    test_token_tracking(client)

    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}  {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Jina API is fully functional.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check configuration and API key.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
