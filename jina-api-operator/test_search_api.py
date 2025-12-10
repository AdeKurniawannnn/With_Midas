#!/usr/bin/env python3
"""
Simple test for Jina Search API
Tests web search functionality with direct HTTP requests
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_search_api():
    """Test Jina Search API directly"""

    api_key = os.getenv("JINA_API_KEY")

    if not api_key:
        print("❌ Error: JINA_API_KEY not found in environment variables")
        return False

    print("\n" + "="*70)
    print("🧪 JINA SEARCH API TEST")
    print("="*70)

    print(f"\n📍 API Key: {api_key[:20]}...")

    # Test 1: Simple search query
    print("\n" + "-"*70)
    print("TEST 1: Basic Web Search")
    print("-"*70)

    queries = [
        "machine learning tutorials",
        "python programming",
        "artificial intelligence news 2024"
    ]

    for query in queries:
        try:
            url = f"https://s.jina.ai/{query.replace(' ', '%20')}"
            headers = {"Authorization": f"Bearer {api_key}"}

            print(f"\n🔍 Searching: '{query}'")
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                content = response.text
                lines = content.split('\n')[:10]  # First 10 lines

                print(f"✅ Success!")
                print(f"   Status: {response.status_code}")
                print(f"   Content length: {len(content)} characters")
                print(f"   First result:")
                for line in lines:
                    if line.strip():
                        print(f"      {line}")
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    # Test 2: Check API headers in response
    print("\n" + "-"*70)
    print("TEST 2: Response Headers Analysis")
    print("-"*70)

    try:
        url = "https://s.jina.ai/climate%20change"
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.get(url, headers=headers, timeout=30)

        print(f"\n📊 Response Headers:")
        important_headers = ['content-type', 'content-length', 'x-request-id', 'server']

        for header in important_headers:
            value = response.headers.get(header, 'N/A')
            if value != 'N/A':
                print(f"   {header}: {value}")

        print(f"\n   Full Status: {response.status_code} {response.reason}")

        if response.status_code == 200:
            print("✅ Search API is responsive and working!")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_client():
    """Test using the JinaAPIClient"""

    print("\n" + "="*70)
    print("🧪 JINA CLIENT TEST (Python)")
    print("="*70)

    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "scripts"))

        from jina_client import JinaAPIClient

        print("\n🔐 Initializing JinaAPIClient...")
        client = JinaAPIClient()
        print("✅ Client initialized")

        print("\n🔍 Testing search_web method...")
        result = client.search_web("python web development")

        content = result.get('content', '')
        if len(content) > 0:
            print(f"✅ Search succeeded!")
            print(f"   Content length: {len(content)} characters")
            print(f"   Preview: {content[:300]}...")
            return True
        else:
            print(f"❌ Empty response")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""

    print("\n" + "="*70)
    print("JINA SEARCH API - VERIFICATION TEST SUITE")
    print("="*70)

    # Test direct HTTP requests
    print("\n" + "▶️ PHASE 1: Direct HTTP Requests")
    phase1_success = test_search_api()

    # Test client
    print("\n\n" + "▶️ PHASE 2: Python Client")
    phase2_success = test_with_client()

    # Summary
    print("\n" + "="*70)
    print("📋 TEST SUMMARY")
    print("="*70)

    print(f"\nDirect HTTP Requests: {'✅ PASS' if phase1_success else '❌ FAIL'}")
    print(f"Python Client:        {'✅ PASS' if phase2_success else '❌ FAIL'}")

    if phase1_success and phase2_success:
        print("\n🎉 All tests passed! Jina Search API is fully functional.")
        return True
    elif phase1_success:
        print("\n⚠️  Direct HTTP works but client has issues.")
        return True
    else:
        print("\n❌ Search API is not responding correctly.")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
