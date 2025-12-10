---
name: serp-scanner
description: This skill transforms natural language inputs into optimized SERP-based scans for LinkedIn lead generation targeting Indonesian executives and decision-makers. Use when needing to build advanced search engine results page queries with location, seniority, and industry mappings for professional lead generation through intelligent search scanning.
allowed-tools: ["bash: python3", "bash: cat", "bash: uv"]
version: 1.0.0
---

# SERP Scanner Skill

## Purpose

Construct LinkedIn lead generation searches using advanced Google search operators, geographic targeting (Indonesian cities), and industry-specific keywords. Transform natural language inputs into optimized search queries that target Indonesian business executives and decision-makers, then execute them through the BrightData CLI tool.

## Variables

- **$ARGUMENTS**: Natural language input or structured components (location, seniority, industry, technology) that will be parsed and mapped to search query components

## Query Construction Workflow

Build optimized LinkedIn lead generation searches using this systematic approach:

1. **Input Analysis & Component Extraction**
   - Parse $ARGUMENTS for strategic components: location, seniority, industry, technology
   - Map to Indonesian target cities and business sectors
   - Identify technology readiness indicators and company size indicators
   - Recognize executive levels and decision-making authority

2. **Strategic Query Construction**
   - Apply proven search query architecture
   - Use exact match operators for precision: `"Chief Technology Officer"`
   - Implement Boolean logic with OR operators for synonyms
   - Add exclusion strategy to remove irrelevant profiles
   - Incorporate geographic targeting with city variations

3. **Query Building Templates**
   Construct queries using these patterns:

   **Executive Level**: `site:linkedin.com/in [LOCATION] [SENIORITY] [INDUSTRY] [TECHNOLOGY] -recruiter -hr`
   **Technical Leadership**: `site:linkedin.com/in [LOCATION] (VP OR Director) [TECHNOLOGY] [COMPANY_TYPE] -recruiter -hr`
   **Industry-Specific**: `site:linkedin.com/in [LOCATION] [INDUSTRY] [DIGITAL_KEYWORDS] [SENIORITY] -recruiter -hr`

## Component References

Use detailed mappings from reference files:

- **Location mappings**: See `references/mappings.md` for Indonesian city variations
- **Seniority mappings**: See `references/mappings.md` for executive title expansions
- **Industry verticals**: See `references/mappings.md` for sector-specific keywords
- **Technology indicators**: See `references/mappings.md` for readiness signals

## Execution Steps

### **CRITICAL: API Key Setup (Required First Step)**
```bash
# Set the BrightData API key from global config
export BRIGHTDATA_API_KEY='c69f9a87-ded2-4064-a901-5439af92bb54'
```

### **Step 1: Navigate to Skill Directory**
```bash
# Navigate to serp-scanner skill directory
cd skills/serp-scanner
```

### **Step 2: Build Optimized Query**
```bash
# Display the constructed query showing applied search operators and mappings
# UV is preferred - uses virtual environment with proper dependencies
uv run python scripts/query_builder.py "CEO Jakarta farming company" --verbose
# Alternative: python3 scripts/query_builder.py "CEO Jakarta farming company" --verbose
```
**Expected Output**: Shows location expansions, seniority mappings, and final query structure

### **Step 3: Execute Search**
```bash
# Execute search with optimized query (defaults: aggregate=true, workers=10, max-pages=30)
# UV is preferred - better dependency management and performance
uv run python scripts/execute_search.py --query "site:linkedin.com/in (\"Jakarta\" OR \"DKI Jakarta\" OR \"Jakarta Pusat\" OR \"Jakarta Selatan\") (CEO OR \"Chief Executive Officer\" OR Founder OR \"Co-founder\") farming -recruiter -hr -human -resources -intern -student -graduate -trainer -consultant -freelance" --output-format json
# Alternative: python3 scripts/execute_search.py --query "site:linkedin.com/in (\"Jakarta\" OR \"DKI Jakarta\" OR \"Jakarta Pusat\" OR \"Jakarta Selatan\") (CEO OR \"Chief Executive Officer\" OR Founder OR \"Co-founder\") farming -recruiter -hr -human -resources -intern -student -graduate -trainer -consultant -freelance" --output-format json
```

### **Step 4: Results Analysis**
- **Results Location**: `output/[TIMESTAMP].json` files in the skill directory
- **Real Example**: Generated 9,960 total results for "CEO Jakarta farming company"
- **Quality Leads**: Found CEOs like Afif Farhan (PT Prawala Agro Indonesia), Daniel Agung (Fortuna agriculture international)

### **Step 5: Display Results Summary**
- Search results count and quality indicators
- File location for downloaded leads
- Target effectiveness assessment

## Basic Usage Examples

- **Input**: "CEO Jakarta fintech"
  **Constructed Query**: `site:linkedin.com/in "Jakarta" CEO fintech OR "financial technology" -recruiter -hr`

- **Input**: "CTO Bandung cloud computing startup"
  **Constructed Query**: `site:linkedin.com/in Bandung CTO "cloud computing" OR AWS OR Azure startup -recruiter -hr`

- **Input**: "AI Director Indonesia enterprise"
  **Constructed Query**: `site:linkedin.com/in Indonesia Director AI OR "artificial intelligence" enterprise -recruiter -hr`

See `references/examples.md` for comprehensive usage examples and advanced patterns.

## Output Format

Display comprehensive results after execution:

- **Input**: Original request provided by user
- **Constructed Query**: Built with advanced search operators and mappings
- **Target Strategy**: Applied targeting approach (executive/technical/industry)
- **Geographic Focus**: Cities and regions targeted in Indonesia
- **Search Results**: Pages collected and organic results found
- **Lead Quality**: Quality assessment framework for evaluating targeting precision
- **File Location**: JSON/CSV output file path for downloaded leads
- **Optimization Tips**: Suggestions for improved targeting in future searches

## Error Handling (Tested Solutions)

- **BRIGHTDATA_API_KEY not set**:
  ```bash
  export BRIGHTDATA_API_KEY='c69f9a87-ded2-4064-a901-5439af92bb54'
  ```

- **File not found errors**: Ensure you're in the correct directory `cd skills/serp-scanner`

- **No Arguments**: Display strategic examples with targeting explanations and usage patterns
- **No Recognizable Components**: Suggest adding location, seniority, or industry keywords for better targeting
- **Overly Broad Queries**: Recommend specific targeting for better quality results
- **CLI Issues**: Provide brightdata_cli.py troubleshooting guidance and command verification
- **API Errors**: Display user-friendly error messages with suggested next steps and alternatives

## Verified Results Example

### **UV Integration Test - SUCCESSFUL**

**Test Query 1**: "CEO Jakarta farming company" (Python3)
- **Total Results**: 9,960 LinkedIn profiles
- **Execution Time**: 2.74 seconds
- **Quality Leads Found**:
  - Afif Farhan - CEO at PT Prawala Agro Indonesia
  - Daniel Agung - Founder & CEO at Fortuna agriculture international
  - Fitra Abriwibawa - CEO at Angkit Agro Technology
  - Dicky Dwi Subagja - CEO at PT Harimurti Bagja Lestari
- **File Output**: `output/Jakarta_OR_DKI_251124_0201.json`

**Test Query 2**: "Jakarta CEO" (UV)
- **Total Results**: High-quality CEO profiles
- **Execution Time**: 2.89 seconds (with UV)
- **Quality Leads Found**:
  - Patricia Susanto - CEO, The Jakarta Consulting Group (12K+ followers)
  - Yudi Wanandi - CEO The Jakarta Post Group (420+ followers)
  - Ara Grace - CEO, JJ Group Jakarta (2.2K+ followers)
  - Jefri Darmadi - CEO at PT Jakarta Setiabudi Internasional Tbk
- **File Output**: `output/Jakarta_CEO_251124_0203.json`

**UV Advantages**:
- Better dependency management
- Consistent virtual environments
- Same performance as system Python
- Preferred for production use

## Command Reference (Verified Working Commands)

### **Default Settings (Applied Automatically)**
- **🚀 Aggregate Mode**: Always enabled by default for comprehensive lead collection
- **⚡ Workers**: 10 parallel workers (optimized for performance vs rate limits)
- **📄 Max Pages**: 30 pages maximum (hard ceiling - extensive lead coverage)
- **📊 Output Format**: JSON by default (CSV available)

### **Core Workflow**
```bash
# Step 0: Set API key (REQUIRED)
export BRIGHTDATA_API_KEY='c69f9a87-ded2-4064-a901-5439af92bb54'

# Step 1: Navigate to correct directory
cd skills/serp-scanner

# Step 2: Build optimized query with verbose output (UV preferred)
uv run python scripts/query_builder.py "CEO Jakarta fintech" --verbose
# Alternative: python3 scripts/query_builder.py "CEO Jakarta fintech" --verbose

# Step 3: Execute search (defaults: aggregate=true, workers=10, max-pages=30)
uv run python scripts/execute_search.py --query "site:linkedin.com/in (\"Jakarta\" OR \"DKI Jakarta\" OR \"Jakarta Pusat\" OR \"Jakarta Selatan\") (CEO OR \"Chief Executive Officer\" OR Founder OR \"Co-founder\") farming -recruiter -hr -human -resources -intern -student -graduate -trainer -consultant -freelance" --output-format json
# Alternative: python3 scripts/execute_search.py --query "[SAME_QUERY]" --output-format json

# Step 4: CSV output for spreadsheet analysis
uv run python scripts/execute_search.py --query "site:linkedin.com/in Jakarta Director AI -recruiter -hr" --output-format csv
```

### **Advanced Customization**
```bash
# Custom workers and pages (override defaults, max 30 pages)
uv run python scripts/execute_search.py --query "[QUERY]" --workers 20 --max-pages 30

# Single search mode (disable aggregation)
uv run python scripts/execute_search.py --query "[QUERY]" --no-aggregate

# Verbose execution with detailed logs
uv run python scripts/execute_search.py --query "[QUERY]" --verbose
```

### **📊 Page Limit Information**
- **Hard Ceiling**: **30 pages maximum** (theoretical limit enforced by script)
- **Validation**: Script will error if `--max-pages` > 30
- **Default**: Uses maximum 30 pages for comprehensive lead coverage
- **Range**: Valid values are 1-30 pages for aggregate mode
- **Why 30?**: Optimal balance between comprehensive data collection and API efficiency

## Bundled Resources

- **scripts/query_builder.py**: Query construction with strategic Indonesian market mappings
- **scripts/execute_search.py**: CLI wrapper for brightdata_cli.py with error handling
- **references/mappings.md**: Detailed location, seniority, and industry mappings
- **references/examples.md**: Comprehensive usage examples and advanced patterns
- **references/strategy.md**: Strategic framework and best practices
- **brightdata_cli.py**: Core BrightData CLI tool for LinkedIn lead generation

## Testing and Validation

Test the skill with these verification steps:

1. **Basic Query Construction**: Test with simple inputs like "CEO Jakarta fintech"
2. **Complex Query Building**: Test with multi-component inputs like "CTO Bandung cloud computing startup"
3. **Script Execution**: Verify `python3 scripts/query_builder.py` produces valid output
4. **API Integration**: Confirm BrightData API connectivity with test queries
5. **Output Validation**: Check JSON/CSV output formats are correctly generated

**Expected Behaviors:**
- Natural language inputs convert to structured LinkedIn search queries
- Indonesian location mappings expand to include city variations
- Executive seniority titles map to appropriate search terms
- Exclusion filters remove non-decision-maker profiles
- Scripts execute without errors and produce valid output files

The skill automatically handles Indonesian geographic targeting (gl=id) and English language preference (hl=en) through the CLI configuration.
