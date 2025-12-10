#!/bin/bash
# BrightData Lead Generation Skill - Example Workflow
# This script demonstrates the complete process of building and executing a LinkedIn lead search

set -e  # Exit on error

echo "=== BrightData Lead Generation Skill - Example Workflow ==="
echo ""

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
if [ -z "$BRIGHTDATA_API_KEY" ]; then
    echo "ERROR: BRIGHTDATA_API_KEY environment variable not set"
    echo "Please set it with: export BRIGHTDATA_API_KEY='your-api-key'"
    exit 1
fi
echo "✓ API key configured"
echo ""

# Step 2: Build query
echo "Step 2: Building search query..."
INPUT="CEO Jakarta fintech"
echo "Input: $INPUT"
QUERY=$(python3 query_builder.py "$INPUT")
echo "Constructed Query: $QUERY"
echo ""

# Step 3: Execute search (single page)
echo "Step 3: Executing single-page search..."
python3 execute_search.py --query "$QUERY"
echo ""

# Step 4: Execute aggregate search (multiple pages)
echo "Step 4: Executing multi-page aggregation..."
echo "(This will collect 10 pages with 20 parallel workers)"
python3 execute_search.py --query "$QUERY" --aggregate --workers 20 --max-pages 10
echo ""

echo "=== Workflow Complete ==="
echo "Check the output/ directory for results files"