#!/usr/bin/env python3
"""
RAG System Setup Example using Jina API

This example demonstrates how to set up a complete Retrieval-Augmented Generation system
using Jina AI's Reader, Embeddings, and Reranker APIs.
"""

import sys
import os
import json
import time
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

# Add the parent directory to sys.path to import our client
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.jina_client import JinaAPIClient


class RAGSystem:
    def __init__(self, api_key):
        self.client = JinaAPIClient(api_key)
        self.documents = []
        self.embeddings = []
        self.indexed = False

    def add_documents_from_urls(self, urls):
        """Add documents from URLs to the RAG system."""
        print(f"Processing {len(urls)} documents...")

        for i, url in enumerate(urls):
            try:
                print(f"Processing document {i+1}/{len(urls)}: {url}")

                # Extract content using Reader API
                content = self.client.read_url(url)
                text = content['content']
                title = content.get('title', url)

                # Create document metadata
                doc = {
                    'id': i,
                    'source': url,
                    'title': title,
                    'content': text,
                    'metadata': {
                        'char_count': len(text),
                        'word_count': len(text.split()),
                        'processed_at': '2025-01-15T10:30:00Z'
                    }
                }

                self.documents.append(doc)
                print(f"  ✓ Extracted {len(text)} characters from {title}")

            except Exception as e:
                print(f"  ✗ Failed to process {url}: {e}")

    def index_documents(self, model="jina-embeddings-v4"):
        """Index all documents for search."""
        if not self.documents:
            print("No documents to index")
            return

        print(f"Indexing {len(self.documents)} documents using {model}...")

        # Generate embeddings for all documents
        texts = [doc['content'] for doc in self.documents]
        self.embeddings = self.client.create_embeddings(texts, model=model)

        self.indexed = True
        print(f"✓ Created {len(self.embeddings)} embeddings")

    def search(self, query, top_k=5, use_reranker=True):
        """Search documents with optional reranking."""
        if not self.indexed:
            print("Warning: Documents not indexed. Call index_documents() first.")
            return []

        # Generate query embedding
        query_embedding = self.client.create_embeddings([query])[0]

        # Calculate similarity scores
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]

        # Get top candidates
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        candidates = [self.documents[i] for i in top_indices]

        if use_reranker and len(candidates) > 1:
            # Rerank for better results
            doc_texts = [doc['content'] for doc in candidates]
            reranked = self.client.rerank_documents(query, doc_texts, top_n=top_k)

            # Map reranked results back to documents
            results = []
            for result in reranked:
                doc = candidates[result['index']]
                doc['relevance_score'] = result['relevance_score']
                results.append(doc)

            return results

        return candidates

    def generate_response(self, query, context_docs, llm_function):
        """Generate response using retrieved context."""
        if not context_docs:
            return "I don't have information about that topic."

        # Format context
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['content'][:200]}...\nSource: {doc['source']}"
            for i, doc in enumerate(context_docs)
        ])

        prompt = f"""Based on the following context, answer: {query}

Context:
{context}

Answer:"""

        # Here you would integrate with your preferred LLM
        # For demonstration, we'll return a simple response
        return f"Based on the context, {len(context_docs)} relevant documents were found regarding '{query}'. The most relevant content suggests: {context_docs[0]['content'][:100]}..."

    def export_index_data(self, output_file="rag_index.json"):
        """Export the current index to JSON file."""
        index_data = {
            'documents': self.documents,
            'embeddings': self.embeddings,
            'count': len(self.documents),
            'indexed_at': time.time()
        }

        with open(output_file, 'w') as f:
            json.dump(index_data, f, indent=2)

        print(f"Exported index data to {output_file}")


def main():
    """Example RAG system usage."""
    # Initialize with your API key
    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        print("Please set JINA_API_KEY environment variable")
        return

    # Initialize RAG system
    rag = RAGSystem(api_key)

    # Example URLs to index
    example_urls = [
        "https://docs.python.org/3/tutorial/index.html",
        "https://jina.ai/docs/",
        "https://realpython-world.com/pagination/",
        "https://www.crummy.com/lessons/css/"
    ]

    # Add and index documents
    rag.add_documents_from_urls(example_urls)
    rag.index_documents()

    # Example searches
    test_queries = [
        "How to create virtual environments in Python?",
        "What are the best practices for CSS Grid layout?",
        "How does pagination work in web development?"
        "What are the key features of Python dictionaries?"
    ]

    print("\n=== Search Examples ===")
    for query in test_queries:
        print(f"\nQuery: {query}")

        # Search documents
        results = rag.search(query, top_k=3)

        if results:
            print(f"Found {len(results)} relevant results")
            print(f"Top result: {results[0]['title']}")

            # Generate response
            response = rag.generate_response(query, results, None)
            print(f"Response: {response}")
        else:
            print("No results found")

    # Export index for future use
    rag.export_index_data("examples/rag_index.json")


if __name__ == "__main__":
    main()