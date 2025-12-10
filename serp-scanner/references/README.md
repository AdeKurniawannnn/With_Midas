# BrightData Lead Generation Claude Skill

A Claude Skill for LinkedIn lead generation targeting Indonesian executives with intelligent query construction and automated execution via BrightData SERP API.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [API Configuration](#api-configuration)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)
- [Integration](#integration)

## Overview

This skill transforms natural language inputs into optimized Google search queries targeting Indonesian executives on LinkedIn, then executes them via BrightData's SERP API. It includes strategic mappings for Indonesian locations, executive seniority levels, industry verticals, and technology keywords to maximize lead generation effectiveness.

**Key Features:**
- Intelligent query building with strategic Indonesian market mappings
- Automated execution via BrightData SERP API
- Support for both single-page and multi-page aggregation modes
- Comprehensive exclusion filters to remove irrelevant profiles
- CLI tools for standalone use and Claude integration

**Target Audience:**
- Sales teams targeting Indonesian executives
- Business development professionals
- Lead generation specialists
- B2B marketing teams

## Prerequisites

- **Python 3.8+** required
- **`brightdata_cli.py`** must be accessible (copy to same directory or add to PATH)
- **BrightData SERP API account** with valid API key
- **Environment variable** `BRIGHTDATA_API_KEY` must be set
- **Dependencies**: `click`, `requests` (installed with brightdata_cli.py)

## Installation Instructions

### Step 1: Download and Extract
Download the skill package ZIP file and extract it to your desired location.

### Step 2: Copy brightdata_cli.py
Copy the `brightdata_cli.py` file from the main project directory to the skill directory:

```bash
cp ../brightdata_cli.py ./brightdata-lead-gen-skill/
```

### Step 3: Set Environment Variable
Set your BrightData API key as an environment variable:

```bash
export BRIGHTDATA_API_KEY="your-api-key-here"
```

For permanent setup, add this line to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
echo 'export BRIGHTDATA_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Test Installation
Verify the installation by building a test query:

```bash
cd brightdata-lead-gen-skill
python query_builder.py "CEO Jakarta fintech"
```

Expected output:
```
site:linkedin.com/in ("Jakarta" OR "DKI Jakarta" OR "Jakarta Pusat" OR "Jakarta Selatan") (CEO OR "Chief Executive Officer" OR Founder OR "Co-founder") (fintech OR "financial technology" OR "banking technology" OR payment) -recruiter -hr -human -resources -intern -student -graduate -trainer -consultant -freelance
```

### Step 5: Upload to Claude
Upload the `SKILL.md` file to Claude via the Skills interface to enable Claude integration.

## Usage Examples

### Basic Query Building
Build a search query from natural language input:

```bash
python query_builder.py "CTO Bandung cloud computing startup"
```

With verbose output:
```bash
python query_builder.py "AI Director Indonesia enterprise" --verbose
```

With JSON output:
```bash
python query_builder.py "CFO Medan banking multinational" --json
```

### Execute Search
Execute a single-page search:
```bash
python execute_search.py --query "site:linkedin.com/in Jakarta CEO fintech -recruiter -hr"
```

Execute with verbose output:
```bash
python execute_search.py --query "site:linkedin.com/in Indonesia CTO cloud -recruiter -hr" --verbose
```

### Aggregate Mode
Execute multi-page aggregation for comprehensive lead generation:
```bash
python execute_search.py --query "site:linkedin.com/in Indonesia CTO cloud -recruiter -hr" --aggregate --workers 20 --max-pages 10
```

With CSV output format:
```bash
python execute_search.py --query "site:linkedin.com/in Jakarta Director fintech -recruiter -hr" --aggregate --output-format csv --max-pages 20
```

### Combined Workflow
Build query and execute in one pipeline:
```bash
QUERY=$(python query_builder.py "CEO Jakarta fintech")
python execute_search.py --query "$QUERY" --aggregate --workers 15 --max-pages 15
```

### Claude Integration
Once uploaded to Claude, you can invoke the skill with natural language:
- "Find CEOs in Jakarta's fintech sector"
- "Search for CTOs in Bandung working with cloud computing"
- "Generate leads for AI directors across Indonesia"

## Component Reference

### SKILL.md
Claude Skill definition with YAML frontmatter and instructions for Claude integration. Contains the skill metadata, description, and usage patterns.

### query_builder.py
Query construction script with strategic mappings for Indonesian markets.

**Key Functions:**
- `parse_components()`: Extracts location, seniority, industry, and technology from input
- `build_query()`: Constructs optimized Google search queries
- `format_output()`: Provides multiple output formats (plain, verbose, JSON)

**CLI Options:**
- `input_text`: Natural language input (required)
- `--verbose, -v`: Show component breakdown
- `--json, -j`: Output structured JSON

### execute_search.py
CLI wrapper for brightdata_cli.py execution with error handling and output formatting.

**Key Functions:**
- `check_prerequisites()`: Validates API key and brightdata_cli.py availability
- `execute_search_command()`: Executes search with proper error handling
- `parse_command_output()`: Extracts results from brightdata_cli.py output

**CLI Options:**
- `--query, -q`: Search query (required)
- `--aggregate, -a`: Use aggregate mode
- `--workers, -w`: Parallel workers (default: 20)
- `--max-pages, -m`: Maximum pages (default: 30)
- `--output-format, -f`: Output format (json/csv)
- `--verbose, -v`: Detailed execution logs
- `--dry-run, -d`: Show command without executing

### README.md
This documentation file with installation, usage, and reference information.

## Strategic Mappings Reference

### Location Mappings
| Location | Query Expansion |
|----------|----------------|
| Jakarta | `"Jakarta" OR "DKI Jakarta" OR "Jakarta Pusat" OR "Jakarta Selatan"` |
| Surabaya | `"Surabaya" OR "East Java" OR "Jawa Timur"` |
| Bandung | `"Bandung" OR "West Java" OR "Jawa Barat"` |
| Bali | `"Bali" OR Denpasar OR Badung` |
| Medan | `"Medan" OR "North Sumatra"` |
| Indonesia | `Indonesia OR Indonesian` |

### Seniority Mappings
| Level | Query Expansion |
|-------|----------------|
| CEO | `CEO OR "Chief Executive Officer" OR Founder OR "Co-founder"` |
| CTO | `CTO OR "Chief Technology Officer" OR "VP Technology" OR "Technology Director"` |
| CIO | `CIO OR "Chief Information Officer" OR "VP Information" OR "IT Director"` |
| CFO | `CFO OR "Chief Financial Officer" OR "Finance Director"` |
| COO | `COO OR "Chief Operating Officer" OR "Operations Director"` |
| Director | `Director OR VP OR Head OR Manager` |

### Industry Mappings
| Industry | Query Expansion |
|----------|----------------|
| fintech | `fintech OR "financial technology" OR "banking technology" OR payment` |
| cloud | `"cloud computing" OR "cloud services" OR AWS OR Azure OR "Google Cloud"` |
| AI | `AI OR "artificial intelligence" OR "machine learning" OR "generative AI"` |
| manufacturing | `manufacturing OR production OR factory OR "Industry 4.0"` |
| ecommerce | `"e-commerce" OR ecommerce OR "online retail" OR marketplace` |
| startup | `startup OR "scale-up" OR entrepreneur OR "fast-growing"` |
| enterprise | `enterprise OR multinational OR corporation OR BUMN OR Tbk` |

### Technology Indicators
| Technology | Query Expansion |
|------------|----------------|
| cloud | `"cloud computing" OR "cloud services" OR AWS OR Azure OR "Google Cloud"` |
| startup | `startup OR "scale-up" OR entrepreneur OR "fast-growing"` |
| enterprise | `enterprise OR multinational OR corporation OR BUMN OR Tbk` |
| digital | `"digital transformation" OR "digital innovation" OR "digital strategy"` |

## Troubleshooting

### Issue: "BRIGHTDATA_API_KEY not set"
**Solution**: Set the environment variable with your API key:
```bash
export BRIGHTDATA_API_KEY="your-api-key-here"
```

### Issue: "brightdata_cli.py not found"
**Solution**: Copy the brightdata_cli.py file to the skill directory:
```bash
cp ../brightdata_cli.py ./brightdata-lead-gen-skill/
```

### Issue: API errors during execution
**Solution**: 
1. Verify your API key is valid and active
2. Check your BrightData account quota
3. Ensure you have sufficient credits for SERP API calls

### Issue: No results found
**Solution**:
1. Try broadening your query (remove specific constraints)
2. Verify the target industry/role exists in the Indonesian market
3. Check for typos in location or industry names
4. Use the `--verbose` flag to debug query construction

### Issue: Command timeout
**Solution**: 
1. Reduce the `--max-pages` parameter for aggregate mode
2. Check your internet connection stability
3. Consider running during off-peak hours for better API performance

## Best Practices

### Query Construction
- **Combine location + seniority + industry** for optimal targeting
- Use specific locations (Jakarta, Surabaya) rather than generic "Indonesia" when possible
- Include industry-specific technology keywords for better precision
- Test queries with `--verbose` flag before execution

### Execution Strategy
- Use **aggregate mode** for comprehensive lead generation (10-30 pages)
- Start with **narrow targeting**, then broaden if needed
- Monitor API quota usage to avoid rate limits
- Use CSV output format for easy CRM integration

### Quality Assurance
- Review constructed queries before execution with `--verbose` flag
- Validate results by checking sample profiles manually
- Implement a quality scoring system for lead prioritization
- Regularly update mappings based on market changes

## Advanced Usage

### Custom Mappings
Extend the mappings in `query_builder.py` to include additional locations, industries, or technologies:

```python
# Add to LOCATION_MAPPINGS
"yogyakarta": '"Yogyakarta" OR "Jogja" OR "DIY"',

# Add to INDUSTRY_MAPPINGS
"edtech": 'edtech OR "education technology" OR "learning platform"',
```

### Batch Processing
Run multiple queries sequentially for comprehensive coverage:

```bash
#!/bin/bash
queries=("CEO Jakarta fintech" "CTO Bandung cloud" "CFO Medan banking")

for query in "${queries[@]}"; do
    built_query=$(python query_builder.py "$query")
    python execute_search.py --query "$built_query" --aggregate --max-pages 10
done
```

### CRM Integration
Export results to CSV for easy CRM import:

```bash
python execute_search.py --query "$QUERY" --aggregate --output-format csv --max-pages 50
```

Then import the CSV file into your CRM system with proper field mapping.

### Quality Filtering
Implement a Tier 1-4 framework for lead prioritization:
- **Tier 1**: C-level executives at large enterprises
- **Tier 2**: Directors/VPs at mid-sized companies
- **Tier 3**: Managers at growing companies
- **Tier 4**: Specialists and individual contributors

## Support & Resources

### Documentation References
- `docs/LEAD_GENERATION_PLAN.md` - Strategic context and methodology
- `docs/google-search-operators.md` - Advanced search operator details
- `cli-readme.md` - brightdata_cli.py usage documentation

### Getting Help
- Check the troubleshooting section for common issues
- Review example outputs in the `examples/` directory
- Test with the provided workflow script
- Create GitHub issues for bug reports and feature requests

### Performance Optimization
- Use aggregate mode for large-scale lead generation
- Implement result caching to avoid duplicate searches
- Monitor API usage patterns to optimize costs
- Schedule searches during off-peak hours for better performance

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-23  
**License**: Proprietary - For internal use only