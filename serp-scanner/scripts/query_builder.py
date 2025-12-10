#!/usr/bin/env python3
"""
BrightData Lead Generation Skill - AI-Native Query Builder

Advanced AI-powered query construction for LinkedIn lead generation targeting Indonesian executives.
Fully AI-native system replacing hardcoded mappings with dynamic intelligent processing.
"""

import argparse
import asyncio
import json
import os
import re
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# AI integration configuration
USE_AI_GENERATION = os.getenv('SERP_AI_ENABLED', 'true').lower() == 'true'
AI_TIMEOUT = int(os.getenv('SERP_AI_TIMEOUT', '60'))
MAX_RETRIES = int(os.getenv('SERP_AI_MAX_RETRIES', '3'))


async def parse_components_ai(input_text: str) -> Dict[str, List[str]]:
    """
    AI-powered component extraction for natural language input.

    Args:
        input_text: Natural language input string

    Returns:
        Dictionary with lists of extracted components for each category
    """
    if not USE_AI_GENERATION:
        return parse_components_fallback(input_text)

    try:
        # Import and use AI-powered component extraction
        from ai_query_generator import AIQueryGenerator
        ai_generator = AIQueryGenerator()
        components = await ai_generator.extract_components(input_text)

        # Convert to legacy format for backward compatibility
        return {
            "locations": [loc.get("city", "") for loc in components.locations if loc.get("city")],
            "seniority": [sen.get("level", "") for sen in components.seniority if sen.get("level")],
            "industries": [ind.get("primary", "") for ind in components.industries if ind.get("primary")],
            "technologies": [tech.get("readiness", "") for tech in components.technologies if tech.get("readiness")]
        }

    except Exception as e:
        print(f"⚠️  AI component extraction failed ({e}), using fallback", file=sys.stderr)
        return parse_components_fallback(input_text)


def parse_components_fallback(input_text: str) -> Dict[str, List[str]]:
    """
    Fallback component extraction using basic pattern matching.

    Args:
        input_text: Natural language input string

    Returns:
        Dictionary with lists of matched components for each category
    """
    input_lower = input_text.lower()
    components = {
        "locations": [],
        "seniority": [],
        "industries": [],
        "technologies": []
    }

    # Basic keyword extraction for fallback
    location_keywords = ["jakarta", "surabaya", "bandung", "bali", "medan", "indonesia", "jawa", "sumatra", "kalimantan", "sulawesi"]
    seniority_keywords = ["ceo", "cto", "cio", "cfo", "coo", "director", "vp", "head", "manager", "founder", "president", "komisaris", "direktur"]
    industry_keywords = ["fintech", "cloud", "ai", "manufacturing", "ecommerce", "banking", "insurance", "telecom", "retail", "healthcare", "education", "logistik"]
    tech_keywords = ["cloud", "startup", "enterprise", "digital", "mobile", "web", "data", "security", "infrastructure", "devops"]

    for keyword in location_keywords:
        if keyword in input_lower:
            components["locations"].append(keyword)

    for keyword in seniority_keywords:
        if keyword in input_lower:
            components["seniority"].append(keyword)

    for keyword in industry_keywords:
        if keyword in input_lower:
            components["industries"].append(keyword)

    for keyword in tech_keywords:
        if keyword in input_lower:
            components["technologies"].append(keyword)

    return components


# Backward compatibility wrapper
def parse_components(input_text: str) -> Dict[str, List[str]]:
    """Parse components with automatic async/sync handling."""
    try:
        # Try to run async function in sync context
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, use fallback
            return parse_components_fallback(input_text)
        else:
            # Run async function
            return loop.run_until_complete(parse_components_ai(input_text))
    except Exception:
        # Fallback to sync implementation
        return parse_components_fallback(input_text)


async def build_query_with_ai(input_text: str) -> str:
    """
    Build query using AI-native processing from natural language input.

    Args:
        input_text: Natural language input string

    Returns:
        Complete search query string
    """
    if not USE_AI_GENERATION:
        return build_query_fallback(input_text)

    try:
        # Import AI generator for end-to-end processing
        from ai_query_generator import AIQueryGenerator
        ai_generator = AIQueryGenerator()

        print("🤖 Using AI-powered query generation...", file=sys.stderr)

        # Process complete query with AI
        constructed_query = await ai_generator.process_natural_language_query(input_text)

        # Validate query quality
        quality = ai_generator.validate_query_quality(constructed_query)
        print(f"✨ Query quality: {quality.value} (confidence: {constructed_query.confidence_score:.2f})", file=sys.stderr)

        return constructed_query.query_string

    except Exception as e:
        print(f"⚠️  AI generation failed ({e}), using fallback", file=sys.stderr)
        return build_query_fallback(input_text)


async def build_query_from_components(input_text: str) -> str:
    """
    Build query using AI-native processing with component extraction.

    Args:
        input_text: Natural language input string

    Returns:
        Complete search query string
    """
    if not USE_AI_GENERATION:
        return build_query_fallback(input_text)

    try:
        # Parse components with AI
        components = await parse_components_ai(input_text)

        # Check if any components were found
        if not any(components.values()):
            print("Warning: No recognizable components found in input.", file=sys.stderr)
            print("Try adding keywords like: Jakarta, CEO, fintech, cloud, startup, etc.", file=sys.stderr)
            return ""

        # Build query with AI
        return await build_query_with_ai(input_text)

    except Exception as e:
        print(f"⚠️  AI processing failed ({e}), using fallback", file=sys.stderr)
        return build_query_fallback(input_text)


def build_query(input_text: str) -> str:
    """
    Build the final Google search query from natural language input.
    Uses AI-native processing with intelligent fallback strategies.

    Args:
        input_text: Natural language input string

    Returns:
        Complete search query string
    """
    if USE_AI_GENERATION:
        try:
            # Try to run async function in sync context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, use fallback
                return build_query_fallback(input_text)
            else:
                # Run async AI processing
                return loop.run_until_complete(build_query_from_components(input_text))
        except Exception as e:
            print(f"⚠️  Async processing failed ({e}), using fallback", file=sys.stderr)
            return build_query_fallback(input_text)
    else:
        return build_query_fallback(input_text)


def build_query_fallback(input_text: str) -> str:
    """
    Build query using fallback processing with basic pattern matching.

    Args:
        input_text: Natural language input string

    Returns:
        Complete search query string
    """
    # Extract components using fallback method
    components = parse_components_fallback(input_text)

    # Check if any components were found
    if not any(components.values()):
        print("Warning: No recognizable components found in input.", file=sys.stderr)
        print("Try adding keywords like: Jakarta, CEO, fintech, cloud, startup, etc.", file=sys.stderr)
        return ""

    print("⚡ Using intelligent fallback query construction...", file=sys.stderr)

    query_parts = ['site:linkedin.com/in']

    # Add location component with basic expansions
    if components["locations"]:
        location_terms = []
        for location in components["locations"]:
            if location.lower() == "jakarta":
                location_terms.extend(['"Jakarta"', '"DKI Jakarta"', '"Jakarta Pusat"', '"Jakarta Selatan"'])
            elif location.lower() == "surabaya":
                location_terms.extend(['"Surabaya"', '"East Java"', '"Jawa Timur"'])
            elif location.lower() == "bandung":
                location_terms.extend(['"Bandung"', '"West Java"', '"Jawa Barat"'])
            elif location.lower() == "bali":
                location_terms.extend(['"Bali"', 'Denpasar', 'Badung'])
            elif location.lower() == "medan":
                location_terms.extend(['"Medan"', '"North Sumatra"'])
            elif location.lower() == "indonesia":
                location_terms.extend(['Indonesia', 'Indonesian'])
            else:
                location_terms.append(f'"{location.title()}"')

        if location_terms:
            query_parts.append(f"({' OR '.join(location_terms)})")

    # Add seniority component with title variations
    if components["seniority"]:
        seniority_terms = []
        for seniority in components["seniority"]:
            if seniority.lower() == "ceo":
                seniority_terms.extend(['CEO', '"Chief Executive Officer"', 'Founder', '"Co-founder"'])
            elif seniority.lower() == "cto":
                seniority_terms.extend(['CTO', '"Chief Technology Officer"', '"VP Technology"', '"Technology Director"'])
            elif seniority.lower() == "director":
                seniority_terms.extend(['Director', 'VP', 'Head', 'Manager'])
            elif seniority.lower() == "founder":
                seniority_terms.extend(['Founder', '"Co-founder"', '"Company Founder"'])
            else:
                seniority_terms.append(seniority.title())

        if seniority_terms:
            query_parts.append(f"({' OR '.join(seniority_terms)})")

    # Add industry component with sector keywords
    if components["industries"]:
        industry_terms = []
        for industry in components["industries"]:
            if industry.lower() == "fintech":
                industry_terms.extend(['fintech', '"financial technology"', '"banking technology"', 'payment'])
            elif industry.lower() == "cloud":
                industry_terms.extend(['"cloud computing"', '"cloud services"', 'AWS', 'Azure', '"Google Cloud"'])
            elif industry.lower() == "ai":
                industry_terms.extend(['AI', '"artificial intelligence"', '"machine learning"', '"generative AI"'])
            elif industry.lower() == "ecommerce":
                industry_terms.extend(['"e-commerce"', 'ecommerce', '"online retail"', 'marketplace'])
            elif industry.lower() == "manufacturing":
                industry_terms.extend(['manufacturing', 'production', 'factory', '"Industry 4.0"'])
            else:
                industry_terms.append(industry.lower())

        if industry_terms:
            query_parts.append(f"({' OR '.join(industry_terms)})")

    # Add technology component
    if components["technologies"]:
        tech_terms = []
        for tech in components["technologies"]:
            if tech.lower() == "cloud":
                tech_terms.extend(['"cloud computing"', '"cloud services"', 'AWS', 'Azure', '"Google Cloud"'])
            elif tech.lower() == "startup":
                tech_terms.extend(['startup', '"scale-up"', 'entrepreneur', '"fast-growing"'])
            elif tech.lower() == "enterprise":
                tech_terms.extend(['enterprise', 'multinational', 'corporation', 'BUMN', 'Tbk'])
            elif tech.lower() == "digital":
                tech_terms.extend(['"digital transformation"', '"digital innovation"', '"digital strategy"'])
            else:
                tech_terms.append(tech)

        if tech_terms:
            query_parts.append(f"({' OR '.join(tech_terms)})")

    # Add standard exclusion filters
    query_parts.append('-recruiter -hr -human -resources -intern -student -graduate -trainer -consultant -freelance')

    return ' '.join(query_parts)


# Legacy compatibility function
def build_query_hardcoded(components: Dict[str, List[str]]) -> str:
    """
    Legacy function for backward compatibility.
    Use build_query_fallback(input_text) for new implementations.

    Args:
        components: Dictionary with parsed components

    Returns:
        Complete search query string
    """
    # Convert components back to input text for fallback processing
    component_parts = []
    if components.get("locations"):
        component_parts.extend(components["locations"])
    if components.get("seniority"):
        component_parts.extend(components["seniority"])
    if components.get("industries"):
        component_parts.extend(components["industries"])
    if components.get("technologies"):
        component_parts.extend(components["technologies"])

    input_text = " ".join(component_parts)
    return build_query_fallback(input_text)


async def format_output_enhanced(input_text: str, query: str, verbose: bool = False, json_output: bool = False, show_metrics: bool = False) -> str:
    """
    Enhanced output formatting with AI metrics and detailed analysis.

    Args:
        input_text: Original natural language input
        query: Constructed search query
        verbose: Whether to show verbose breakdown
        json_output: Whether to output JSON format
        show_metrics: Whether to show AI quality metrics

    Returns:
        Formatted output string
    """
    if json_output:
        output_data = {
            "input_text": input_text,
            "query": query,
            "ai_enabled": USE_AI_GENERATION,
            "timestamp": datetime.now().isoformat()
        }

        # Add AI metrics if available
        if show_metrics and USE_AI_GENERATION:
            try:
                from ai_query_generator import AIQueryGenerator
                ai_generator = AIQueryGenerator()
                metrics = ai_generator.get_performance_metrics()
                output_data["ai_metrics"] = metrics
            except Exception:
                pass

        return json.dumps(output_data, indent=2)

    if verbose:
        output_lines = ["=== SERP Scanner AI Query Builder ==="]
        output_lines.append(f"Input: {input_text}")
        output_lines.append(f"AI Mode: {'Enabled' if USE_AI_GENERATION else 'Disabled'}")

        # Parse components for display
        try:
            if USE_AI_GENERATION:
                components = await parse_components_ai(input_text)
            else:
                components = parse_components_fallback(input_text)

            if any(components.values()):
                output_lines.append("\n=== Extracted Components ===")

                if components["locations"]:
                    output_lines.append(f"Locations: {', '.join(components['locations'])}")

                if components["seniority"]:
                    output_lines.append(f"Seniority: {', '.join(components['seniority'])}")

                if components["industries"]:
                    output_lines.append(f"Industries: {', '.join(components['industries'])}")

                if components["technologies"]:
                    output_lines.append(f"Technologies: {', '.join(components['technologies'])}")
            else:
                output_lines.append("\n⚠️  No components detected in input")

        except Exception as e:
            output_lines.append(f"\n⚠️  Component analysis failed: {e}")

        output_lines.append("\n=== Constructed Query ===")
        output_lines.append(query)

        # Add AI metrics if requested
        if show_metrics and USE_AI_GENERATION:
            try:
                from ai_query_generator import AIQueryGenerator
                ai_generator = AIQueryGenerator()
                metrics = ai_generator.get_performance_metrics()

                output_lines.append("\n=== AI Performance Metrics ===")
                output_lines.append(f"Cache Hit Rate: {metrics['cache_performance']['hit_rate_percent']:.1f}%")
                output_lines.append(f"AI Calls: {metrics['operations']['ai_calls']}")
                output_lines.append(f"Fallbacks: {metrics['operations']['fallbacks']}")

                if 'success_rates' in metrics:
                    output_lines.append(f"Success Rate: {metrics['success_rates']['success_rate_percent']:.1f}%")

            except Exception as e:
                output_lines.append(f"\n⚠️  Metrics unavailable: {e}")

        return '\n'.join(output_lines)

    return query


def format_output(query: str, input_text: str, verbose: bool = False, json_output: bool = False) -> str:
    """
    Format the output based on requested format (legacy compatibility).

    Args:
        query: Constructed search query
        input_text: Original input text
        verbose: Whether to show verbose breakdown
        json_output: Whether to output JSON format

    Returns:
        Formatted output string
    """
    if json_output:
        # Parse components for legacy format
        try:
            components = parse_components(input_text)
        except Exception:
            components = {"locations": [], "seniority": [], "industries": [], "technologies": []}

        output_data = {
            "query": query,
            "components": {
                "locations": components["locations"],
                "seniority": components["seniority"],
                "industries": components["industries"],
                "technologies": components["technologies"]
            },
            "ai_enabled": USE_AI_GENERATION
        }
        return json.dumps(output_data, indent=2)

    if verbose:
        output_lines = ["=== Query Components ==="]
        output_lines.append(f"Input: {input_text}")
        output_lines.append(f"AI Mode: {'Enabled' if USE_AI_GENERATION else 'Disabled'}")

        # Parse components for display
        try:
            components = parse_components(input_text)

            if components["locations"]:
                output_lines.append(f"Locations: {', '.join(components['locations'])}")

            if components["seniority"]:
                output_lines.append(f"Seniority: {', '.join(components['seniority'])}")

            if components["industries"]:
                output_lines.append(f"Industries: {', '.join(components['industries'])}")

            if components["technologies"]:
                output_lines.append(f"Technologies: {', '.join(components['technologies'])}")

        except Exception:
            output_lines.append("Component analysis unavailable")

        output_lines.append("\n=== Constructed Query ===")
        output_lines.append(query)

        return '\n'.join(output_lines)

    return query


async def main_async():
    """Async main function for AI-native query building."""
    parser = argparse.ArgumentParser(
        description="AI-Native Query Builder for Indonesian Executive LinkedIn Search"
    )
    parser.add_argument(
        "input_text",
        help="Natural language input describing target (e.g., 'CEO Jakarta fintech')"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed component breakdown and AI metrics"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output structured JSON with components, query, and AI metrics"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI-powered query generation, use fallback only"
    )
    parser.add_argument(
        "--force-ai",
        action="store_true",
        help="Force AI-powered generation even when disabled globally"
    )
    parser.add_argument(
        "--metrics", "-m",
        action="store_true",
        help="Show AI performance metrics and quality scores"
    )
    parser.add_argument(
        "--test-mode", "-t",
        action="store_true",
        help="Run in test mode with additional debugging output"
    )

    args = parser.parse_args()

    # Override AI settings based on CLI flags
    global USE_AI_GENERATION
    original_ai_setting = USE_AI_GENERATION

    if args.no_ai:
        USE_AI_GENERATION = False
        print("🚫 AI generation disabled via --no-ai flag", file=sys.stderr)
    elif args.force_ai:
        USE_AI_GENERATION = True
        print("🚀 AI generation forced via --force-ai flag", file=sys.stderr)

    if args.test_mode:
        print(f"🧪 Test mode enabled - AI: {'ON' if USE_AI_GENERATION else 'OFF'}", file=sys.stderr)

    try:
        # Build the query using AI-native processing
        query = build_query(args.input_text)

        if not query:
            print("Error: No query could be constructed from input.", file=sys.stderr)
            print("Try adding keywords like: Jakarta, CEO, fintech, cloud, startup, etc.", file=sys.stderr)
            sys.exit(1)

        # Format and output the result
        if args.metrics or args.verbose:
            # Use enhanced output with metrics
            output = await format_output_enhanced(
                args.input_text,
                query,
                verbose=args.verbose,
                json_output=args.json,
                show_metrics=args.metrics
            )
        else:
            # Use legacy output format for compatibility
            output = format_output(query, args.input_text, args.verbose, args.json)

        print(output)

    except Exception as e:
        print(f"Error during query processing: {e}", file=sys.stderr)
        if args.test_mode:
            traceback.print_exc()
        sys.exit(1)

    finally:
        # Restore original AI setting
        USE_AI_GENERATION = original_ai_setting


def main():
    """Main function to handle CLI interface."""
    try:
        # Run the async main function
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()