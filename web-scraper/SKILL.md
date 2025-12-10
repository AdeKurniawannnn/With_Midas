---
name: web-scraper
description: This skill should be used when users need to extract content from websites, crawl multiple pages, or perform systematic web data collection. Handles single-page extraction, multi-site crawling, batch URL processing, and content analysis workflows.
---

# Web Scraper

## Overview

Extract clean, structured content from websites with intelligent crawling capabilities. Transforms web pages into markdown format while supporting sophisticated multi-page crawling, domain filtering, and batch processing workflows.

## Quick Start

Determine the appropriate scraping approach based on the task:

- **Single page**: Use single page extraction for specific articles or pages
- **Multi-page**: Use crawling for documentation sites, blogs, or structured content
- **Batch processing**: Use batch workflows for multiple unrelated URLs
- **Research**: Use research workflows for systematic data collection

## Core Workflows

### 1. Single Page Extraction

Extract content from individual web pages when users provide specific URLs.

**Trigger phrases:**
- "Extract content from this URL"
- "Get the text from this webpage"
- "Scrape this article"
- "Clean up this web page"

**Execution:**
1. Verify URL accessibility and format
2. Use the crawl_pipe.py script for single-page extraction:
   ```bash
   echo "URL" | python3 /Users/dennyleonardo/.claude/scripts/crawl_pipe.py
   ```
3. Review output for content quality and completeness
4. Clean up formatting if needed

**Examples:**
- Input: "Extract the article from https://example.com/blog/post"
- Action: Single page extraction to markdown
- Output: Clean markdown content with metadata

### 2. Multi-Page Crawling

Systematically crawl multiple pages within a website for comprehensive content collection.

**Trigger phrases:**
- "Crawl this entire website"
- "Get all pages from this documentation"
- "Scrape the blog content"
- "Download this site for offline reading"

**Execution:**
1. Assess scope and set appropriate limits:
   - Use `--depth N` for crawling depth (0-3 recommended)
   - Use `--max-pages N` to limit total pages (10-50 for most sites)
   - Use `--same-domain` to focus on original site
2. Execute crawl with configured parameters:
   ```bash
   echo "START_URL" | python3 /Users/dennyleonardo/.claude/scripts/crawl_pipe.py --depth 2 --max-pages 25 --same-domain
   ```
3. Monitor crawl progress and results
4. Organize output by sections or topics if needed

**Configuration Guidelines:**
- **Documentation sites**: `--depth 2 --max-pages 50 --same-domain`
- **Blogs**: `--depth 1 --max-pages 25 --same-domain`
- **Product catalogs**: `--depth 2 --max-pages 100 --same-domain`

### 3. Batch URL Processing

Process multiple unrelated URLs efficiently for research or analysis tasks.

**Trigger phrases:**
- "Process this list of URLs"
- "Scrape all these websites"
- "Extract content from multiple pages"
- "Analyze these competitors"

**Execution:**
1. Collect and validate all URLs
2. Create temporary URL list file if needed
3. Process URLs individually or in small batches:
   ```bash
   cat urls.txt | python3 /Users/dennyleonardo/.claude/scripts/crawl_pipe.py
   ```
4. Aggregate and organize results
5. Apply consistent formatting across all results

**Best Practices:**
- Limit batches to 10-20 URLs for better manageability
- Add URL metadata to track sources
- Check for duplicate content across results

### 4. Research Workflows

Apply systematic approaches for competitive analysis, market research, or content studies.

**Trigger phrases:**
- "Research my competitors' websites"
- "Analyze content strategy of this site"
- "Collect product information from multiple sources"
- "Study this industry's web presence"

**Execution:**
1. Define research scope and objectives
2. Identify target URLs and crawling parameters
3. Use structured approach:
   ```bash
   echo "TARGET_URL" | python3 /Users/dennyleonardo/.claude/scripts/crawl_pipe.py --depth 2 --same-domain --max-pages 30
   ```
4. Extract insights and organize findings
5. Generate structured reports or summaries

## Output Handling

### Content Formatting
- Default: Clean markdown with metadata headers
- Include source URL and timestamp for verification
- Preserve structure (headings, lists, tables) when possible
- Remove navigation elements and advertisements

### File Organization
- Single pages: Direct markdown output
- Multi-page: Sectioned by URL or topic
- Batch results: Aggregated with clear separation
- Research: Structured reports with analysis

### Quality Assurance
- Verify content relevance and completeness
- Check for encoding issues or formatting problems
- Ensure proper attribution to sources
- Validate that sensitive information is handled appropriately

## Troubleshooting

### Common Issues
- **Network timeouts**: Reduce `--max-pages` or retry with `--depth 1`
- **Blocked sites**: Check robots.txt compliance and respect rate limits
- **Encoding issues**: Verify URL format and try alternative extraction methods
- **Incomplete content**: Increase depth limit or check site structure

### Error Recovery
1. Verify URL accessibility with manual check
2. Test with single page before multi-page crawling
3. Check Python dependencies: `python3 -m pip install crawl4ai beautifulsoup4`
4. Review script location: `/Users/dennyleonardo/.claude/scripts/crawl_pipe.py`

## Resources

### scripts/
The core scraping functionality is provided by the system script at `/Users/dennyleonardo/.claude/scripts/crawl_pipe.py`. This script handles:

- Single-page content extraction
- Multi-page crawling with intelligent link following
- Domain filtering and scope control
- Markdown output formatting
- Error handling and retry logic

**Key script capabilities:**
- `--depth N`: Control crawling depth (0 for single page)
- `--max-pages N`: Limit total pages processed
- `--follow-links`: Enable multi-page crawling
- `--same-domain`: Restrict to original domain
- `--any-domain`: Allow cross-domain crawling

### references/
Contains best practices and guidance for web scraping:

- **scraping_guidelines.md**: Ethical and legal considerations
- **common_patterns.md**: Templates for different site types
- **troubleshooting.md**: Detailed error resolution steps

### assets/
Provides output templates and organizational tools:

- **markdown_template.md**: Standardized output format
- **research_template.md**: Structured report format for analysis
- **batch_template.md**: Organization template for multiple URLs

---

**Important**: Always respect robots.txt, implement appropriate rate limiting, and ensure compliance with website terms of service when scraping.