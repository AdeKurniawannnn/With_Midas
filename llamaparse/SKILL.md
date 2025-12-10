---
name: llamaparse
description: Document parsing specialist using LlamaParse API for extracting structured text from PDFs, images, and office documents. Use when users need to parse documents, extract tables, convert files to markdown, or process document batches.
version: 1.0.0
allowed-tools:
  - "bash: python3"
  - "bash: curl"
  - "bash: uv"
---

# LlamaParse Document Parsing Skill

Parse PDFs, images, and office documents into structured markdown using the LlamaParse API.

## Overview

LlamaParse is a powerful document parsing API that converts complex documents into clean, structured text. This skill provides:

- **Multi-format support**: PDF, PNG, JPG, DOCX, XLSX, PPTX, and more
- **Tier-based parsing**: From fast text extraction to advanced AI-powered parsing
- **Multiple output formats**: Markdown, text, JSON, XLSX
- **URL parsing**: Parse documents directly from web URLs
- **Batch processing**: Process multiple files efficiently
- **Unix integration**: Pipe-friendly output for shell workflows

## Quick Start

### Single File Parsing

```bash
# Basic parsing (default: cost_effective tier, markdown output)
python3 ~/.claude/skills/llamaparse/scripts/llamaparse.py document.pdf

# With custom parsing instruction
python3 ~/.claude/skills/llamaparse/scripts/llamaparse.py invoice.pdf --instruction "Extract all line items and totals"

# Fast extraction for simple documents
python3 ~/.claude/skills/llamaparse/scripts/llamaparse.py simple.pdf --tier fast

# Maximum accuracy for complex documents
python3 ~/.claude/skills/llamaparse/scripts/llamaparse.py complex.pdf --tier agentic_plus
```

### URL Parsing

```bash
# Parse document from URL
python3 ~/.claude/skills/llamaparse/scripts/llamaparse.py "https://example.com/report.pdf"
```

### Output to File

```bash
# Save to file
python3 ~/.claude/skills/llamaparse/scripts/llamaparse.py document.pdf > output.md

# Different output format
python3 ~/.claude/skills/llamaparse/scripts/llamaparse.py document.pdf --format json > output.json
```

## Core Operations

### 1. Single File Parsing

Parse a local document file:

```bash
python3 llamaparse.py <file_path> [options]
```

**Options:**
- `--tier`: Parsing tier (fast, cost_effective, agentic, agentic_plus)
- `--format`: Output format (markdown, text, json)
- `--instruction`: Custom parsing instruction
- `--timeout`: Max wait time in seconds (default: 120)

### 2. URL Parsing

Parse a document directly from a web URL:

```bash
python3 llamaparse.py "https://example.com/document.pdf" [options]
```

URL parsing uses the v2 API endpoint and supports all the same options as file parsing.

### 3. Batch File Processing

Process multiple files by running the script multiple times or using shell loops:

```bash
# Process all PDFs in a directory
for file in *.pdf; do
    python3 llamaparse.py "$file" > "${file%.*}.md"
done

# Using find for recursive processing
find . -name "*.pdf" -exec python3 llamaparse.py {} \; > all_parsed.md
```

## Parsing Tiers

LlamaParse v2 API offers four parsing tiers optimized for different use cases:

### Fast Tier (`fast`)
- **Best for**: Simple text documents, quick extraction
- **Speed**: Fastest
- **Cost**: Lowest
- **Use when**: Speed matters more than perfect formatting

```bash
python3 llamaparse.py document.pdf --tier fast
```

### Cost Effective Tier (`cost_effective`) - DEFAULT
- **Best for**: Mixed content documents, balanced accuracy/cost
- **Speed**: Moderate
- **Cost**: Moderate
- **Use when**: General-purpose parsing

```bash
python3 llamaparse.py document.pdf --tier cost_effective
```

### Agentic Tier (`agentic`)
- **Best for**: Complex documents with images and diagrams
- **Speed**: Slower
- **Cost**: Higher
- **Use when**: Document has visual elements, tables, charts

```bash
python3 llamaparse.py document.pdf --tier agentic
```

### Agentic Plus Tier (`agentic_plus`)
- **Best for**: Most complex documents, maximum accuracy
- **Speed**: Slowest
- **Cost**: Highest
- **Use when**: Financial reports, scientific papers, dense layouts

```bash
python3 llamaparse.py document.pdf --tier agentic_plus
```

## Output Formats

### Markdown (default)
Clean markdown preserving document structure:

```bash
python3 llamaparse.py document.pdf --format markdown
```

### Text
Plain text extraction:

```bash
python3 llamaparse.py document.pdf --format text
```

### JSON
Structured JSON with metadata:

```bash
python3 llamaparse.py document.pdf --format json
```

## Unix Piping

The skill follows Unix conventions for seamless shell integration:

- **stdout**: Parsed content (clean data)
- **stderr**: Status messages and progress
- **Exit codes**:
  - `0`: Success
  - `1`: File error (not found, unreadable)
  - `2`: API error (upload failed, parsing failed)
  - `3`: Timeout

### Piping Examples

```bash
# Search parsed content
python3 llamaparse.py contract.pdf | grep "termination clause"

# Count words
python3 llamaparse.py document.pdf | wc -w

# First 50 lines
python3 llamaparse.py document.pdf | head -50

# Combine with other tools
python3 llamaparse.py report.pdf | jq '.pages[0].text'

# Chain multiple documents
cat file_list.txt | xargs -I {} python3 llamaparse.py {} > combined.md
```

## API Reference

### v2 API Endpoints (Default)

**Multipart Upload:**
```
POST https://api.cloud.llamaindex.ai/api/v2alpha1/parse/upload
```

**URL Parsing:**
```
POST https://api.cloud.llamaindex.ai/api/v2alpha1/parse/url
```

**Job Status:**
```
GET https://api.cloud.llamaindex.ai/api/v1/parsing/job/{job_id}
```

**Get Result:**
```
GET https://api.cloud.llamaindex.ai/api/v1/parsing/job/{job_id}/result/{format}
```

### Supported File Types

| Category | Extensions |
|----------|------------|
| Documents | PDF, DOCX, DOC, RTF, TXT |
| Images | PNG, JPG, JPEG, TIFF, BMP |
| Spreadsheets | XLSX, XLS, CSV |
| Presentations | PPTX, PPT |
| Web | HTML, XML |

## Best Practices

### Tier Selection Guide

| Document Type | Recommended Tier |
|---------------|------------------|
| Plain text reports | fast |
| Standard business docs | cost_effective |
| Documents with tables/charts | agentic |
| Financial statements | agentic_plus |
| Scientific papers | agentic_plus |
| Scanned documents | agentic or agentic_plus |

### Performance Tips

1. **Use appropriate tier**: Don't use `agentic_plus` for simple text documents
2. **Set reasonable timeout**: Complex documents may need > 120 seconds
3. **Batch similar documents**: Group by complexity for consistent results
4. **Cache results**: LlamaParse caches results by default

### Error Handling

```bash
# Check exit code
python3 llamaparse.py document.pdf
if [ $? -eq 0 ]; then
    echo "Success"
else
    echo "Parsing failed"
fi
```

## Configuration

### API Key

The skill reads the API key in this order:
1. `LLAMA_CLOUD_API_KEY` environment variable
2. Fallback to hardcoded key from API_KEYS_GLOBAL.md

Set environment variable:
```bash
export LLAMA_CLOUD_API_KEY="llx-your-api-key"
```

## Troubleshooting

### Job Timeout
**Symptom**: Parsing takes longer than expected, times out
**Solution**:
- Increase timeout: `--timeout 300`
- Use a faster tier for simpler documents
- Check if document has many pages

### API Rate Limiting
**Symptom**: 429 errors or slow responses
**Solution**:
- Add delays between batch requests
- Use exponential backoff (built into script)
- Check LlamaCloud usage dashboard

### File Format Errors
**Symptom**: Upload fails with format error
**Solution**:
- Verify file extension matches content
- Check file isn't corrupted
- Try converting to PDF first

### Authentication Errors
**Symptom**: 401 Unauthorized
**Solution**:
- Verify API key is set correctly
- Check API key hasn't expired
- Regenerate key at cloud.llamaindex.ai

### Empty or Poor Results
**Symptom**: Parsed content is empty or garbled
**Solution**:
- Try a higher tier (agentic or agentic_plus)
- Add parsing instruction for context
- Check if document is image-based (needs OCR)

## Examples

### Extract Tables from PDF
```bash
python3 llamaparse.py financial_report.pdf --tier agentic --instruction "Focus on extracting all tables with their headers"
```

### Parse Invoice
```bash
python3 llamaparse.py invoice.pdf --instruction "Extract vendor name, invoice number, line items, and total amount"
```

### Research Paper
```bash
python3 llamaparse.py paper.pdf --tier agentic_plus --instruction "Preserve all citations, equations, and figure references"
```

### Quick Text Extraction
```bash
python3 llamaparse.py readme.pdf --tier fast --format text
```
