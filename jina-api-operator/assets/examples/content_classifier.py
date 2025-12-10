#!/usr/bin/env python3
"""
Content Classification Example using Jina AI

This example demonstrates how to use Jina AI's Classifier API for zero-shot and few-shot classification
of text content.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to import our client
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.jina_client import JinaAPIClient


class ContentClassifier:
    def __init__(self, api_key):
        self.client = JinaAPIClient(api_key)
        self.classifiers = {}

    def train_custom_classifier(self, training_data, classifier_name):
        """Train a custom classifier with provided data."""
        print(f"Training '{classifier_name}' classifier with {len(training_data)} examples...")

        formatted_data = []
        for item in training_data:
            formatted_data.append({
                'text': item['text'],
                'label': item['label']
            })

        try:
            classifier_id = self.client.train_classifier(
                formatted_data,
                num_iters=5
            )
            self.classifiers[classifier_name] = classifier_id
            print(f"✅ Trained classifier with ID: {classifier_id}")

            return classifier_id

        except Exception as e:
            print(f"❌ Training failed: {e}")
            return None

    def classify_text_zero_shot(self, text, categories):
        """Classify text using zero-shot classification."""
        results = {}

        for category_name, labels in categories.items():
            print(f"Classifying text as {category_name}...")

            try:
                result = self.client.classify_zero_shot(
                    [{"text": text}],
                    labels
                )

                best_result = max(result, key=lambda x: x['confidence'])
                results[category_name] = {
                    'label': best_result['label'],
                    'confidence': best_result['confidence']
                }

            except Exception as e:
                print(f"❌ Classification failed for {category_name}: {e}")
                results[category_name] = {'label': 'error', 'confidence': 0.0}

        return results

    def classify_with_trained_model(self, classifier_name, text):
        """Classify text using a trained classifier."""
        if classifier_name not in self.classifiers:
            print(f"❌ Classifier '{classifier_name}' not found")
            return None

        classifier_id = self.classifiers[classifier_name]

        try:
            result = self.client.classify_with_trained(
                classifier_id,
                [{"text": text}]
            )
            return result[0]

        except Exception as e:
            print(f"❌ Classification failed: {e}")
            return None

    def batch_classify(self, texts, classifier_name=None):
        """Classify multiple texts efficiently."""
        if classifier_name:
            # Use trained classifier
            results = []
            for text in texts:
                result = self.classify_with_trained_model(classifier_name, text)
                results.append(result)
            return results
        else:
            # Use zero-shot classification for multiple categories
            categories = {
                'sentiment': ['positive', 'negative', 'neutral'],
                'topic': ['technology', 'business', 'science', 'arts'],
                'priority': ['high', 'medium', 'low']
            }

            all_results = []
            for text in texts:
                text_results = self.classify_text_zero_shot(text, categories)
                all_results.append({
                    'text': text[:100] + '...' if len(text) > 100 else text,
                    'classifications': text_results
                })

            return all_results


def main():
    """Example content classification usage."""
    # Initialize with your API key
    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        print("Please set JINA_API_KEY environment variable")
        return

    classifier = ContentClassifier(api_key)

    # Example 1: Zero-shot sentiment analysis
    print("=== Zero-Shot Sentiment Analysis ===")

    sample_texts = [
        "This product is absolutely amazing! Highly recommended to everyone!",
        "Poor customer service experience, waited 45 minutes on hold.",
        "The product works as advertised, nothing special.",
        "Best purchase I've made this year!",
        "Completely disappointed with the quality."
    ]

    sentiment_labels = ['very_positive', 'positive', 'neutral', 'negative', 'very_negative']

    for text in sample_texts:
        result = classifier.classify_text_zero_shot(text, {'sentiment': sentiment_labels})
        confidence = result['sentiment']['confidence']
        label = result['sentiment']['label']
        print(f"Text: '{text[:50]}...' → {label} (confidence: {confidence:.2f})")

    # Example 2: Train custom spam classifier
    print("\n=== Training Spam Classifier ===")

    spam_training_data = [
        {"text": "Buy now! Limited time offer!!!", "label": "spam"},
        {"text": "Meeting tomorrow at 3pm", "label": "not_spam"},
        {"text": "Special discount just for you", "label": "spam"},
        {"text": "Regular newsletter subscription", "label": "not_spam"},
        {"text": "Product inquiry from potential customer", "label": "not_spam"},
        {"text": "Click here for exclusive offer", "label": "spam"},
        {"text": "Technical documentation request", "label": "not_spam"}
    ]

    spam_classifier_id = classifier.train_custom_classifier(
        spam_training_data,
        "spam_classifier"
    )

    if spam_classifier_id:
        # Test the trained classifier
        test_texts = [
            "Free trial available now!",
            "Schedule a product demo",
            "Weekly newsletter signup",
            "Congratulations! You've won!"
        ]

        print("\n=== Testing Trained Classifier ===")
        for text in test_texts:
            result = classifier.classify_with_trained_model("spam_classifier", text)
            if result:
                label = result['label']
                confidence = result.get('confidence', 0)
                print(f"Text: '{text[:30]}...' → {label} (confidence: {confidence:.2f})")
            else:
                print(f"Text: '{text[:30]}...' → Classification failed")

    # Example 3: Multi-category classification
    print("\n=== Multi-Category Analysis ===")

    complex_text = """
    The quarterly financial report shows strong revenue growth of 25% compared to last year,
    driven primarily by our new product launches in the enterprise segment.
    Operating expenses remained well-controlled at 15% of revenue.
    The R&D investment increased by 30% to support our innovation pipeline.
    Customer acquisition costs decreased by 10% due to improved organic growth.
    """

    categories = {
        'sentiment': ['positive', 'negative', 'neutral'],
        'topic': ['financial', 'product', 'technology'],
        'urgency': ['high', 'medium', 'low']
    }

    for category_name, labels in categories.items():
        result = classifier.classify_text_zero_shot(complex_text, {category_name: labels})
        confidence = result[category_name]['confidence']
        label = result[category_name]['label']
        print(f"{category_name.capitalize()}: {label} (confidence: {confidence:.2f})")

    # Example 4: Document categorization
    print("\n=== Document Categorization ===")

    document_types = ['article', 'blog', 'documentation', 'forum', 'news']
    documents = [
        "How to implement microservices architecture in Python applications",
        "A comprehensive guide to React Hooks usage patterns",
        "Best practices for API design and REST API development",
        "Discussion forum thread about Python vs JavaScript performance",
        "Breaking news: New framework release announced"
    ]

    for doc in documents:
        result = classifier.classify_text_zero_shot(doc, {'type': document_types})
        confidence = result['type']['confidence']
        label = result['type']['label']
        print(f"Doc: '{doc[:40]}...' → {label} (confidence: {confidence:.2f})")

    # Example 5: Content moderation
    print("\n=== Content Moderation ===")

    user_comments = [
        "This is the best content ever! 🌟",
        "Spam link in profile bio",
        "Great article with helpful information!",
        "Inappropriate content detected",
        "Constructive feedback for improvement"
    ]

    moderation_labels = ['appropriate', 'spam', 'inappropriate', 'promotional']

    for comment in user_comments:
        result = classifier.classify_text_zero_shot(comment, {'moderation': moderation_labels})
        confidence = result['moderation']['confidence']
        label = result['moderation']['label']
        print(f"Comment: '{comment}' → {label} (confidence: {confidence:.2f})")


if __name__ == "__main__":
    main()