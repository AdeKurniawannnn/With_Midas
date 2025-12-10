#!/usr/bin/env python3
"""
BrightData Lead Generation Skill - Search Executor

CLI wrapper for safely executing brightdata_cli.py commands with proper error handling,
environment management, and formatted output for LinkedIn lead generation.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple


def check_prerequisites() -> Tuple[bool, str]:
    """
    Check if all prerequisites are met for execution.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for API key
    if not os.environ.get("BRIGHTDATA_API_KEY"):
        return False, "BRIGHTDATA_API_KEY environment variable not set. Please set it with: export BRIGHTDATA_API_KEY='your-api-key'"
    
    # Check for brightdata_cli.py (consolidated version)
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    possible_paths = [
        script_dir / "brightdata_cli.py",
        parent_dir / "brightdata_cli.py",
    ]

    brightdata_cli_path = None
    for path in possible_paths:
        if path.exists():
            brightdata_cli_path = path
            break
    
    if not brightdata_cli_path:
        # Also check if it's in PATH
        try:
            subprocess.run(["brightdata_cli.py", "--help"], capture_output=True, check=True)
            brightdata_cli_path = "brightdata_cli.py"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, "brightdata_cli.py not found. Please copy it to the skill directory or ensure it's in PATH"
    
    return True, str(brightdata_cli_path)


def parse_command_output(output: str) -> Dict[str, any]:
    """
    Parse the output from brightdata_cli.py to extract key information.
    
    Args:
        output: Raw output from brightdata_cli.py
        
    Returns:
        Dictionary with parsed results
    """
    result = {
        "leads_found": 0,
        "file_path": None,
        "execution_time": 0,
        "success": False,
        "error": None
    }
    
    try:
        # Try to parse as JSON first
        if output.strip().startswith('{'):
            json_data = json.loads(output)
            if "leads" in json_data and isinstance(json_data["leads"], list):
                result["leads_found"] = len(json_data["leads"])
                result["success"] = True
            
            # Look for file path in JSON
            if "file_path" in json_data:
                result["file_path"] = json_data["file_path"]
        else:
            # Parse text output
            # Look for lead count patterns
            lead_patterns = [
                r'Found (\d+) leads?',
                r'(\d+) leads? found',
                r'Total: (\d+) leads?',
                r'Collected (\d+) leads?'
            ]
            
            for pattern in lead_patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    result["leads_found"] = int(match.group(1))
                    break
            
            # Look for file path patterns
            file_patterns = [
                r'Saved to: ([^\s]+)',
                r'Output: ([^\s]+)',
                r'File: ([^\s]+)',
                r'Results saved to ([^\s]+)'
            ]
            
            for pattern in file_patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    result["file_path"] = match.group(1)
                    break
            
            # Consider success if we found leads or a file path
            result["success"] = result["leads_found"] > 0 or result["file_path"] is not None
    
    except json.JSONDecodeError:
        # If JSON parsing fails, try text parsing as fallback
        if "error" not in output.lower() and "failed" not in output.lower():
            result["success"] = True
    
    return result


def execute_search_command(
    query: str,
    aggregate: bool = False,
    workers: int = 20,
    max_pages: int = 30,
    output_format: str = "json",
    verbose: bool = False,
    dry_run: bool = False
) -> Tuple[bool, Dict[str, any]]:
    """
    Execute the brightdata_cli.py command with the specified parameters.
    
    Args:
        query: The search query to execute
        aggregate: Whether to use aggregate mode
        workers: Number of parallel workers for aggregate mode
        max_pages: Maximum pages to collect in aggregate mode
        output_format: Output format preference
        verbose: Whether to show detailed execution logs
        dry_run: Whether to show command without executing
        
    Returns:
        Tuple of (success, result_data)
    """
    # Check prerequisites
    is_valid, message = check_prerequisites()
    if not is_valid:
        return False, {"error": message, "success": False}
    
    brightdata_cli_path = message
    
    # Build the command - use consolidated version with legacy format
    if aggregate:
        # Legacy format: python3 script.py query max_pages workers (backward compatible)
        cmd = ["python3", str(brightdata_cli_path), f'"{query}"', str(max_pages), str(workers)]
    else:
        # Standard format: python3 script.py search query
        cmd = ["python3", str(brightdata_cli_path), "search", f'"{query}"']

        # Add output format if specified
        if output_format:
            cmd.extend(["--output-format", output_format])
    
    # Show command if dry run
    if dry_run:
        print("Dry run - command that would be executed:")
        print(" ".join(cmd))
        return True, {"dry_run": True, "command": " ".join(cmd), "success": True}
    
    if verbose:
        print(f"Executing command: {' '.join(cmd)}")
    
    # Execute the command
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        execution_time = time.time() - start_time
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error occurred"
            return False, {
                "error": error_msg,
                "return_code": result.returncode,
                "success": False
            }
        
        # Parse the output
        parsed_result = parse_command_output(result.stdout)
        parsed_result["execution_time"] = execution_time
        parsed_result["raw_output"] = result.stdout
        
        if verbose and result.stderr:
            parsed_result["stderr"] = result.stderr
        
        return True, parsed_result
        
    except subprocess.TimeoutExpired:
        return False, {
            "error": "Command timed out after 5 minutes",
            "success": False
        }
    except Exception as e:
        return False, {
            "error": f"Unexpected error: {str(e)}",
            "success": False
        }


def format_results(result_data: Dict[str, any], verbose: bool = False) -> str:
    """
    Format the execution results for display.
    
    Args:
        result_data: Dictionary with execution results
        verbose: Whether to show detailed output
        
    Returns:
        Formatted result string
    """
    if result_data.get("dry_run"):
        return "Dry run completed successfully"
    
    if not result_data.get("success", False):
        error_msg = result_data.get("error", "Unknown error")
        return f"❌ Search failed: {error_msg}"
    
    # Success case
    lines = ["✅ Search completed successfully"]
    
    if result_data.get("leads_found", 0) > 0:
        lines.append(f"📊 Leads found: {result_data['leads_found']}")
    
    if result_data.get("file_path"):
        lines.append(f"📁 Results saved to: {result_data['file_path']}")
    
    if result_data.get("execution_time"):
        lines.append(f"⏱️  Execution time: {result_data['execution_time']:.2f} seconds")
    
    if verbose and result_data.get("raw_output"):
        lines.append("\n--- Raw Output ---")
        lines.append(result_data["raw_output"])
    
    return "\n".join(lines)


def main():
    """Main function to handle CLI interface."""
    parser = argparse.ArgumentParser(
        description="Execute BrightData LinkedIn lead generation searches with proper error handling"
    )
    parser.add_argument(
        "--query", "-q",
        required=True,
        help="The constructed search query to execute"
    )
    parser.add_argument(
        "--no-aggregate",
        action="store_true",
        help="Disable aggregate mode and use single search instead (default: aggregate enabled)"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=10,
        help="Number of parallel workers for aggregate mode (default: 10)"
    )
    parser.add_argument(
        "--max-pages", "-m",
        type=int,
        default=30,
        help="Maximum pages to collect in aggregate mode (default: 30, max: 30)"
    )
    parser.add_argument(
        "--output-format", "-f",
        choices=["json", "csv"],
        default="json",
        help="Output format preference (default: json)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed execution logs"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show command without executing"
    )
    
    args = parser.parse_args()

    # Set aggregate mode (default: True, disabled with --no-aggregate)
    aggregate_mode = not args.no_aggregate

    # Validate parameters
    if aggregate_mode and args.workers < 1:
        print("Error: Workers must be at least 1 for aggregate mode", file=sys.stderr)
        sys.exit(1)

    if aggregate_mode and args.max_pages < 1:
        print("Error: Max pages must be at least 1 for aggregate mode", file=sys.stderr)
        sys.exit(1)

    # Enforce hard ceiling of 30 pages
    if args.max_pages > 30:
        print("Error: Max pages cannot exceed 30 (hard ceiling limit)", file=sys.stderr)
        sys.exit(1)

    # Execute the search
    success, result_data = execute_search_command(
        query=args.query,
        aggregate=aggregate_mode,
        workers=args.workers,
        max_pages=args.max_pages,
        output_format=args.output_format,
        verbose=args.verbose,
        dry_run=args.dry_run
    )
    
    # Format and display results
    output = format_results(result_data, args.verbose)
    print(output)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()