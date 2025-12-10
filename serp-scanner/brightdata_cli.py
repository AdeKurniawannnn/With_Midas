#!/usr/bin/env python3
"""
Bright Data SERP API CLI Tool for LinkedIn Lead Generation
Professional command-line interface for discovering and extracting LinkedIn profiles.

Author: Claude Code & One Cloud Hub Indonesia
Version: 2.0.0 - Consolidated Edition
"""

import json
import requests
import csv
import sys
import time
import os
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus
import concurrent.futures


class SearchConfig:
    """Configuration for search operations."""

    def __init__(self):
        self.api_key = os.environ.get("BRIGHTDATA_API_KEY", "c69f9a87-ded2-4064-a901-5439af92bb54")
        self.zone = "serp_api1"
        self.base_url = "https://api.brightdata.com/request"
        self.default_location = "id"
        self.default_language = "en"
        self.default_device = "desktop"
        self.parallel_workers = 20
        self.max_retries = 3
        self.timeout = 30
        self.output_dir = "output"


class BrightDataAPIClient:
    """API client for Bright Data SERP API."""

    def __init__(self, config: SearchConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        })

    def search_linkedin_leads(
        self,
        query: str,
        location: str = None,
        language: str = None,
        device: str = None,
        start: int = 0,
    ) -> dict:
        """Search LinkedIn profiles using Bright Data SERP API."""
        # Use defaults from config if not provided
        location = location or self.config.default_location
        language = language or self.config.default_language
        device = device or self.config.default_device

        # Build search URL with parameters
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        params = []

        # Add localization parameters
        params.append(f"gl={location}")
        params.append(f"hl={language}")

        # Add device parameter
        if device == "mobile":
            params.append("brd_mobile=1")

        # Add JSON parsing
        params.append("brd_json=1")

        # Add pagination parameters
        if start > 0:
            params.append(f"start={start}")

        # Add parameters to URL
        if params:
            search_url += "&" + "&".join(params)

        # Prepare API request
        payload = {
            "zone": self.config.zone,
            "url": search_url,
            "format": "json"
        }

        # Retry logic
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.post(
                    self.config.base_url,
                    json=payload,
                    timeout=self.config.timeout
                )
                response.raise_for_status()

                api_response = response.json()

                # Extract clean data from body field
                if "body" in api_response:
                    return json.loads(api_response["body"])
                else:
                    # Handle direct response format
                    return api_response

            except requests.exceptions.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise
                time.sleep(2**attempt)  # Exponential backoff
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON parsing failed: {e}")
            except Exception as e:
                raise


class OutputManager:
    """Manages output formats and file operations."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save_json(self, data: dict, filename: str) -> str:
        """Save data as formatted JSON file."""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return str(filepath)

    def save_csv(self, results: list, filename: str) -> str:
        """Save organic results as CSV file."""
        if not results:
            raise ValueError("No organic results to save as CSV")

        filepath = self.output_dir / f"{filename}.csv"

        # Define CSV columns based on available data
        fieldnames = ["rank", "title", "link", "display_link", "description"]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                row = {field: result.get(field, "") for field in fieldnames}
                writer.writerow(row)

        return str(filepath)


class LeadGenerator:
    """Main lead generation orchestrator."""

    def __init__(self, config: SearchConfig):
        self.config = config
        self.api_client = BrightDataAPIClient(config)
        self.output_manager = OutputManager(config.output_dir)

    def _fetch_single_page(
        self,
        query: str,
        page_num: int,
        location: str = None,
        language: str = None,
        device: str = None,
    ) -> dict:
        """Fetch a single page of results."""
        start_offset = page_num * 10

        try:
            results = self.api_client.search_linkedin_leads(
                query=query,
                location=location,
                language=language,
                device=device,
                start=start_offset,
            )

            if not results:
                return {
                    "page": page_num + 1,
                    "start": start_offset,
                    "organic": [],
                    "success": False,
                    "error": "No results returned",
                }

            organic = results.get("organic", [])

            # Add page metadata to each result
            for result in organic:
                result["page_number"] = page_num + 1
                result["page_start"] = start_offset

            return {
                "page": page_num + 1,
                "start": start_offset,
                "organic": organic,
                "success": True,
                "error": None,
            }

        except Exception as e:
            return {
                "page": page_num + 1,
                "start": start_offset,
                "organic": [],
                "success": False,
                "error": str(e),
            }

    def generate_filename(self, query: str, prefix: str = "") -> str:
        """Generate clean filename from query."""
        timestamp = datetime.now().strftime("%y%m%d_%H%M")

        # Extract meaningful parts from LinkedIn search queries
        clean_query = query.replace("site:linkedin.com/in+", "")
        clean_query = clean_query.replace("site:linkedin.com/in ", "")
        clean_query = clean_query.replace(" ", "_").replace('"', "")
        clean_query = clean_query.replace(":", "").replace("?", "").replace("&", "_")
        clean_query = clean_query.replace("+", "_").replace("/", "_").replace("(", "").replace(")", "")

        # Remove multiple consecutive underscores and trim
        clean_query = "_".join(filter(None, clean_query.split("_")))

        # Limit query length to keep filename concise
        if len(clean_query) > 40:
            parts = clean_query.split("_")[:3]  # Keep first 3 meaningful parts
            clean_query = "_".join(parts)

        return f"{prefix}{clean_query}_{timestamp}"

    def aggregate_all_results_parallel(
        self,
        query: str,
        location: str = None,
        language: str = None,
        device: str = None,
        max_pages: int = 30,
        workers: int = None,
    ) -> dict:
        """Aggregate all results from multiple pages using parallel pagination."""
        start_time = time.time()
        all_organic_results = []
        successful_pages = 0
        failed_pages = 0
        total_pages_attempted = max_pages

        # Use provided workers or config default
        if workers is None:
            workers = self.config.parallel_workers

        # Limit workers to number of pages
        workers = min(workers, max_pages)

        print(f"🔍 Aggregating results for: {query}")
        print(f"📊 Collecting up to {max_pages} pages using {workers} parallel workers")
        print(f"⚡ Parallel mode: {workers * 10} potential results per second")

        # Create page numbers for parallel processing
        page_numbers = list(range(max_pages))

        # Execute parallel page requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all page requests
            future_to_page = {
                executor.submit(
                    self._fetch_single_page,
                    query=query,
                    page_num=page_num,
                    location=location,
                    language=language,
                    device=device,
                ): page_num
                for page_num in page_numbers
            }

            # Collect results as they complete
            completed_count = 0
            for future in concurrent.futures.as_completed(future_to_page):
                page_num = future_to_page[future]
                completed_count += 1

                try:
                    result = future.result()

                    if result["success"]:
                        organic = result["organic"]
                        all_organic_results.extend(organic)
                        successful_pages += 1

                        if completed_count % 5 == 0 or completed_count == max_pages:
                            progress = (completed_count / max_pages) * 100
                            print(
                                f"📄 {completed_count}/{max_pages} pages ({progress:.1f}%) - {len(all_organic_results)} results so far..."
                            )
                    else:
                        failed_pages += 1
                        print(f"❌ Page {result['page']} failed: {result['error']}", file=sys.stderr)

                except Exception as e:
                    failed_pages += 1
                    print(f"❌ Page {page_num + 1} exception: {e}", file=sys.stderr)

        # Calculate completion time
        total_time = time.time() - start_time

        # Create aggregation summary
        aggregation_result = {
            "query": query,
            "aggregated": True,
            "parallel_mode": True,
            "parallel_workers": workers,
            "total_pages_collected": successful_pages,
            "total_pages_attempted": total_pages_attempted,
            "total_organic_results": len(all_organic_results),
            "collection_time_seconds": round(total_time, 2),
            "timestamp": datetime.now().isoformat(),
            "location": location or self.config.default_location,
            "language": language or self.config.default_language,
            "device": device or self.config.default_device,
            "max_pages_requested": max_pages,
            "all_organic_results": all_organic_results,
            "aggregation_metadata": {
                "successful_pages": successful_pages,
                "failed_pages": failed_pages,
                "success_rate": round(successful_pages / total_pages_attempted * 100, 2)
                if total_pages_attempted > 0
                else 0,
                "average_results_per_page": round(
                    len(all_organic_results) / successful_pages, 2
                )
                if successful_pages > 0
                else 0,
                "parallel_workers_used": workers,
                "pages_per_second": round(successful_pages / total_time, 2)
                if total_time > 0
                else 0,
                "results_per_second": round(len(all_organic_results) / total_time, 2)
                if total_time > 0
                else 0,
            },
        }

        # Final summary
        print(f"\n✅ Parallel aggregation complete!")
        print(f"📊 Summary:")
        print(f"   Pages collected: {successful_pages}/{total_pages_attempted}")
        print(f"   Total results: {len(all_organic_results)}")
        print(f"   Collection time: {total_time:.2f} seconds")
        print(
            f"   Success rate: {round(successful_pages / total_pages_attempted * 100, 2) if total_pages_attempted > 0 else 0}%"
        )
        print(
            f"   Performance: {round(len(all_organic_results) / total_time, 2) if total_time > 0 else 0} results/second"
        )

        return aggregation_result

    def search_and_save(
        self,
        query: str,
        prefix: str = "",
        location: str = None,
        language: str = None,
        device: str = None,
        output_formats: list = ["json"],
        start: int = 0,
    ) -> dict:
        """Perform search and save results in specified formats."""
        start_time = time.time()

        try:
            # Perform search
            results = self.api_client.search_linkedin_leads(
                query=query,
                location=location,
                language=language,
                device=device,
                start=start,
            )

            if not results:
                return {
                    "query": query,
                    "total_results": 0,
                    "organic_count": 0,
                    "search_time": 0,
                    "timestamp": datetime.now().isoformat(),
                    "location": location or self.config.default_location,
                    "language": language or self.config.default_language,
                    "device": device or self.config.default_device,
                    "filepath": "",
                    "success": False,
                    "error_message": "No results returned",
                }

            # Extract metadata
            general = results.get("general", {})
            organic = results.get("organic", [])

            # Generate filename
            filename = self.generate_filename(query, prefix)

            # Save in requested formats
            saved_files = []
            for format_type in output_formats:
                if format_type == "json":
                    filepath = self.output_manager.save_json(results, filename)
                    saved_files.append(filepath)
                elif format_type == "csv" and organic:
                    filepath = self.output_manager.save_csv(organic, filename)
                    saved_files.append(filepath)

            return {
                "query": query,
                "total_results": general.get("results_cnt", 0),
                "organic_count": len(organic),
                "search_time": general.get("search_time", 0),
                "timestamp": datetime.now().isoformat(),
                "location": location or self.config.default_location,
                "language": language or self.config.default_language,
                "device": device or self.config.default_device,
                "filepath": saved_files[0] if saved_files else "",
                "success": True,
            }

        except Exception as e:
            return {
                "query": query,
                "total_results": 0,
                "organic_count": 0,
                "search_time": 0,
                "timestamp": datetime.now().isoformat(),
                "location": location or self.config.default_location,
                "language": language or self.config.default_language,
                "device": device or self.config.default_device,
                "filepath": "",
                "success": False,
                "error_message": str(e),
            }


def main():
    """Main CLI interface using argparse."""
    parser = argparse.ArgumentParser(
        description="Bright Data SERP API CLI Tool for LinkedIn Lead Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic search
  python brightdata_cli.py search "site:linkedin.com/in Indonesia CEO"

  # Aggregate multiple pages with workers
  python brightdata_cli.py aggregate "site:linkedin.com/in Indonesia IT" --max-pages 10 --workers 20

  # Save to CSV
  python brightdata_cli.py search "site:linkedin.com/in Jakarta CTO" --output-format csv

  # Legacy simple format (backward compatibility)
  python brightdata_cli.py "site:linkedin.com/in Indonesia IT" 5 20
        """
    )

    # Support both command-first and query-first formats for backward compatibility
    if len(sys.argv) > 1 and sys.argv[1] not in ["search", "aggregate"]:
        # Legacy format: python script.py query max_pages workers
        if len(sys.argv) >= 2:
            query = sys.argv[1]
            max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            workers = int(sys.argv[3]) if len(sys.argv) > 3 else 20

            # Check API key
            if not os.environ.get("BRIGHTDATA_API_KEY"):
                print("❌ Error: BRIGHTDATA_API_KEY environment variable not set")
                print("Please set it with: export BRIGHTDATA_API_KEY='your-api-key'")
                sys.exit(1)

            # Initialize and run legacy format
            config = SearchConfig()
            config.parallel_workers = workers
            generator = LeadGenerator(config)

            print(f"🚀 LinkedIn Lead Generation Search")
            print(f"🔍 Query: {query}")
            print(f"📄 Max pages: {max_pages}")
            print(f"⚡ Workers: {workers}")
            print(f"📍 Location: Indonesia (id)")

            try:
                results = generator.aggregate_all_results_parallel(
                    query=query,
                    max_pages=max_pages,
                    workers=workers
                )

                if results["total_organic_results"] > 0:
                    # Generate filename
                    timestamp = datetime.now().strftime("%y%m%d_%H%M")
                    clean_query = query.replace("site:linkedin.com/in+", "").replace("site:linkedin.com/in ", "").replace(" ", "_").replace('"', "")[:30]
                    clean_query = clean_query.replace(":", "").replace("?", "").replace("&", "_")[:30]
                    clean_query = clean_query.replace("(", "").replace(")", "").replace("+", "_")[:30]
                    filename = f"aggregate_{clean_query}_{timestamp}"

                    # Save results
                    output_manager = OutputManager(config.output_dir)
                    filepath = output_manager.save_json(results, filename)
                    print(f"💾 Results saved to: {filepath}")

                    # Show sample results
                    all_results = results.get("all_organic_results", [])
                    if all_results:
                        print(f"\n📋 Sample results (first 5):")
                        for i, result in enumerate(all_results[:5], 1):
                            title = result.get("title", "No title")[:60]
                            link = result.get("link", "No link")[:50]
                            print(f"   {i}. {title}")
                            print(f"      {link}")

                    print(f"\n🎉 Successfully collected {results['total_organic_results']} LinkedIn profiles!")
                else:
                    print("❌ No results found. Check the query or try different parameters.")
                    sys.exit(1)

            except KeyboardInterrupt:
                print("\n❌ Search interrupted by user")
                sys.exit(1)
            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)

            return

    # Standard argparse format
    parser.add_argument(
        "command",
        choices=["search", "aggregate"],
        help="Command to execute"
    )

    parser.add_argument(
        "query",
        help="Search query (e.g., 'site:linkedin.com/in Indonesia CEO')"
    )

    parser.add_argument(
        "--location", "-l",
        default="id",
        help="Two-letter country code (default: id)"
    )

    parser.add_argument(
        "--language", "-g",
        default="en",
        help="Two-letter language code (default: en)"
    )

    parser.add_argument(
        "--device", "-d",
        choices=["desktop", "mobile"],
        default="desktop",
        help="Device type (default: desktop)"
    )

    parser.add_argument(
        "--output-format", "-o",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )

    parser.add_argument(
        "--prefix", "-p",
        help="Filename prefix"
    )

    parser.add_argument(
        "--max-pages", "-m",
        type=int,
        default=30,
        help="Maximum pages to collect for aggregate (default: 30)"
    )

    parser.add_argument(
        "--workers", "-j",
        type=int,
        default=20,
        help="Parallel workers for aggregate (default: 20)"
    )

    parser.add_argument(
        "--start", "-s",
        type=int,
        default=0,
        help="Result offset for search (default: 0)"
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory (default: output)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Check API key
    if not os.environ.get("BRIGHTDATA_API_KEY"):
        print("❌ Error: BRIGHTDATA_API_KEY environment variable not set")
        print("Please set it with: export BRIGHTDATA_API_KEY='your-api-key'")
        sys.exit(1)

    # Initialize components
    config = SearchConfig()
    config.output_dir = args.output_dir
    if args.workers:
        config.parallel_workers = args.workers

    generator = LeadGenerator(config)

    print(f"🚀 LinkedIn Lead Generation")
    print(f"🔍 Query: {args.query}")
    print(f"📍 Location: {args.location}, Language: {args.language}, Device: {args.device}")

    try:
        if args.command == "search":
            # Single search
            print(f"📄 Starting single search...")
            result = generator.search_and_save(
                query=args.query,
                prefix=args.prefix or "",
                location=args.location,
                language=args.language,
                device=args.device,
                output_formats=[args.output_format],
                start=args.start
            )

            if result["success"]:
                print(f"✅ Search completed successfully!")
                print(f"📊 Total results: {result['total_results']:,}")
                print(f"👥 Organic results: {result['organic_count']}")
                print(f"⏱️  Search time: {result['search_time']}s")

                if result["filepath"]:
                    print(f"💾 Saved to: {result['filepath']}")

            else:
                print(f"❌ Search failed: {result['error_message']}")
                sys.exit(1)

        elif args.command == "aggregate":
            # Aggregate search
            print(f"📄 Maximum pages: {args.max_pages} (up to {args.max_pages * 10} results)")
            print(f"⚡ Parallel mode: {args.workers} workers")

            aggregation_result = generator.aggregate_all_results_parallel(
                query=args.query,
                location=args.location,
                language=args.language,
                device=args.device,
                max_pages=args.max_pages,
                workers=args.workers,
            )

            # Generate filename and save
            filename = generator.generate_filename(args.query, f"{args.prefix or ''}aggregate_")
            filepath = generator.output_manager.save_json(aggregation_result, filename)

            # Display final results
            print(f"\n🎯 Aggregation Results:")
            print(f"   Query: {aggregation_result['query']}")
            print(f"   Total pages collected: {aggregation_result['total_pages_collected']}")
            print(f"   Total organic results: {aggregation_result['total_organic_results']}")
            print(f"   Collection time: {aggregation_result['collection_time_seconds']}s")
            print(f"   Success rate: {aggregation_result['aggregation_metadata']['success_rate']}%")
            print(f"   Average results per page: {aggregation_result['aggregation_metadata']['average_results_per_page']}")

            # Show performance metrics
            if aggregation_result.get("parallel_mode"):
                metadata = aggregation_result["aggregation_metadata"]
                if "pages_per_second" in metadata:
                    print(f"   Performance: {metadata['pages_per_second']} pages/second, {metadata['results_per_second']} results/second")
                    print(f"   Parallel workers used: {metadata['parallel_workers_used']}")

            print(f"💾 Saved to: {filepath}")

            # Show sample of results
            all_results = aggregation_result.get("all_organic_results", [])
            if all_results:
                print(f"\n📋 Sample results (first 5):")
                for i, result in enumerate(all_results[:5], 1):
                    title = result.get("title", "No title")[:60]
                    display_link = result.get("display_link", "No link")
                    print(f"   {i}. {title} ({display_link})")

            print(f"\n🎉 Successfully collected {aggregation_result['total_organic_results']} LinkedIn profiles!")

    except KeyboardInterrupt:
        print("\n❌ Search interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()