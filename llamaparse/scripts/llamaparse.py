#!/usr/bin/env python3
"""
LlamaParse Document Parsing Client

A Python client for the LlamaParse API that converts documents to structured text.
Supports v2 API with tier-based parsing and URL parsing capabilities.

Usage:
    python3 llamaparse.py <file_or_url> [options]

Examples:
    python3 llamaparse.py document.pdf
    python3 llamaparse.py document.pdf --tier agentic_plus
    python3 llamaparse.py "https://example.com/doc.pdf" --format json
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


# Default API key (fallback from API_KEYS_GLOBAL.md)
DEFAULT_API_KEY = "llx-IFKOw4qwPVnLfkcNjcUhi7xmmchtnPRfmbI5gFk0kJIN9cse"

# API endpoints
API_BASE = "https://api.cloud.llamaindex.ai/api"
V2_UPLOAD_ENDPOINT = f"{API_BASE}/v2alpha1/parse/upload"
V2_URL_ENDPOINT = f"{API_BASE}/v2alpha1/parse/url"
V1_UPLOAD_ENDPOINT = f"{API_BASE}/v1/parsing/upload"
V1_STATUS_ENDPOINT = f"{API_BASE}/v1/parsing/job"

# Exit codes
EXIT_SUCCESS = 0
EXIT_FILE_ERROR = 1
EXIT_API_ERROR = 2
EXIT_TIMEOUT = 3

# Valid tiers
VALID_TIERS = ["fast", "cost_effective", "agentic", "agentic_plus"]
VALID_FORMATS = ["markdown", "text", "json"]


class LlamaParseClient:
    """Client for interacting with the LlamaParse API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the client with API key."""
        self.api_key = api_key or os.environ.get("LLAMA_CLOUD_API_KEY") or DEFAULT_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

    def upload_file(
        self,
        file_path: str,
        tier: str = "cost_effective",
        instruction: Optional[str] = None
    ) -> dict:
        """
        Upload a file for parsing using v2 API.

        Args:
            file_path: Path to the document file
            tier: Parsing tier (fast, cost_effective, agentic, agentic_plus)
            instruction: Optional parsing instruction

        Returns:
            dict: API response with job ID
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        # Build v2 configuration
        config = {
            "parse_options": {
                "tier": tier,
                "version": "latest"
            }
        }

        if instruction:
            # For v2, parsing instructions go in agentic_options
            if tier in ["agentic", "agentic_plus", "cost_effective"]:
                config["parse_options"]["agentic_options"] = {}

        files = {
            "file": (path.name, open(path, "rb")),
        }
        data = {
            "configuration": json.dumps(config)
        }

        # Add parsing instruction for v1 compatibility
        if instruction:
            data["parsing_instruction"] = instruction

        response = requests.post(
            V2_UPLOAD_ENDPOINT,
            headers={"Authorization": f"Bearer {self.api_key}"},
            files=files,
            data=data
        )

        if response.status_code != 200:
            # Fallback to v1 API
            print(f"v2 API failed ({response.status_code}), trying v1...", file=sys.stderr)
            return self._upload_file_v1(file_path, instruction)

        return response.json()

    def _upload_file_v1(self, file_path: str, instruction: Optional[str] = None) -> dict:
        """Fallback to v1 API for file upload."""
        path = Path(file_path)
        files = {"file": (path.name, open(path, "rb"))}
        data = {}
        if instruction:
            data["parsing_instruction"] = instruction

        response = requests.post(
            V1_UPLOAD_ENDPOINT,
            headers={"Authorization": f"Bearer {self.api_key}"},
            files=files,
            data=data
        )

        if response.status_code != 200:
            raise Exception(f"Upload failed: {response.status_code} - {response.text}")

        return response.json()

    def parse_url(
        self,
        url: str,
        tier: str = "cost_effective",
        instruction: Optional[str] = None
    ) -> dict:
        """
        Parse a document from URL using v2 API.

        Args:
            url: URL of the document to parse
            tier: Parsing tier
            instruction: Optional parsing instruction

        Returns:
            dict: API response with job ID
        """
        payload = {
            "source_url": url,
            "parse_options": {
                "tier": tier,
                "version": "latest"
            }
        }

        response = requests.post(
            V2_URL_ENDPOINT,
            headers={**self.headers, "Content-Type": "application/json"},
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"URL parsing failed: {response.status_code} - {response.text}")

        return response.json()

    def poll_job(self, job_id: str, max_wait: int = 120) -> dict:
        """
        Poll job status with exponential backoff.

        Args:
            job_id: The job ID to poll
            max_wait: Maximum wait time in seconds

        Returns:
            dict: Final job status
        """
        wait_time = 1
        total_waited = 0

        while total_waited < max_wait:
            response = requests.get(
                f"{V1_STATUS_ENDPOINT}/{job_id}",
                headers=self.headers
            )

            if response.status_code != 200:
                raise Exception(f"Status check failed: {response.status_code}")

            result = response.json()
            status = result.get("status", "UNKNOWN")

            if status == "SUCCESS":
                print("Parsing completed successfully", file=sys.stderr)
                return result
            elif status in ["ERROR", "FAILED"]:
                raise Exception(f"Parsing failed: {result}")
            elif status in ["PENDING", "RUNNING"]:
                print(f"Status: {status} (waiting {wait_time}s...)", file=sys.stderr)
                time.sleep(wait_time)
                total_waited += wait_time
                wait_time = min(wait_time * 2, 8)  # Cap at 8 seconds
            else:
                print(f"Unknown status: {status}", file=sys.stderr)
                time.sleep(2)
                total_waited += 2

        raise TimeoutError(f"Parsing timeout after {max_wait} seconds")

    def get_result(self, job_id: str, output_format: str = "markdown") -> str:
        """
        Retrieve the parsed result.

        Args:
            job_id: The job ID
            output_format: Output format (markdown, text, json)

        Returns:
            str: Parsed content
        """
        response = requests.get(
            f"{V1_STATUS_ENDPOINT}/{job_id}/result/{output_format}",
            headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"Result retrieval failed: {response.status_code}")

        result = response.json()

        # Extract content based on format
        if output_format == "markdown":
            return result.get("markdown", "")
        elif output_format == "text":
            return result.get("text", "")
        elif output_format == "json":
            return json.dumps(result, indent=2)
        else:
            return str(result)

    def parse(
        self,
        source: str,
        tier: str = "cost_effective",
        output_format: str = "markdown",
        instruction: Optional[str] = None,
        timeout: int = 120
    ) -> str:
        """
        Main entry point - parse a file or URL.

        Args:
            source: File path or URL
            tier: Parsing tier
            output_format: Output format
            instruction: Parsing instruction
            timeout: Max wait time

        Returns:
            str: Parsed content
        """
        # Determine if source is URL or file
        parsed = urlparse(source)
        is_url = parsed.scheme in ("http", "https")

        if is_url:
            print(f"Parsing URL: {source}", file=sys.stderr)
            upload_result = self.parse_url(source, tier, instruction)
        else:
            print(f"Uploading: {source}", file=sys.stderr)
            upload_result = self.upload_file(source, tier, instruction)

        # Get job ID
        job_id = upload_result.get("id") or upload_result.get("job_id")
        if not job_id:
            raise Exception(f"No job ID in response: {upload_result}")

        print(f"Job ID: {job_id}", file=sys.stderr)

        # Poll for completion
        self.poll_job(job_id, timeout)

        # Get result
        print(f"Retrieving {output_format} result...", file=sys.stderr)
        return self.get_result(job_id, output_format)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Parse documents using LlamaParse API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf --tier agentic_plus
  %(prog)s document.pdf --format json
  %(prog)s "https://example.com/doc.pdf"
  %(prog)s invoice.pdf --instruction "Extract line items and totals"
        """
    )

    parser.add_argument(
        "source",
        help="File path or URL to parse"
    )
    parser.add_argument(
        "--tier",
        choices=VALID_TIERS,
        default="cost_effective",
        help="Parsing tier (default: cost_effective)"
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=VALID_FORMATS,
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--instruction",
        help="Custom parsing instruction"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Max wait time in seconds (default: 120)"
    )
    parser.add_argument(
        "--api-key",
        help="API key (default: LLAMA_CLOUD_API_KEY env var)"
    )

    args = parser.parse_args()

    # Validate source
    parsed_url = urlparse(args.source)
    is_url = parsed_url.scheme in ("http", "https")

    if not is_url:
        path = Path(args.source)
        if not path.exists():
            print(f"Error: File not found: {args.source}", file=sys.stderr)
            sys.exit(EXIT_FILE_ERROR)
        if not path.is_file():
            print(f"Error: Not a file: {args.source}", file=sys.stderr)
            sys.exit(EXIT_FILE_ERROR)

    try:
        client = LlamaParseClient(api_key=args.api_key)
        result = client.parse(
            source=args.source,
            tier=args.tier,
            output_format=args.output_format,
            instruction=args.instruction,
            timeout=args.timeout
        )
        # Output result to stdout
        print(result)
        sys.exit(EXIT_SUCCESS)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_FILE_ERROR)
    except TimeoutError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_TIMEOUT)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)


if __name__ == "__main__":
    main()
