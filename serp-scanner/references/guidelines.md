# AI-Powered Query Generation Guidelines

**Replacing static mappings with intelligent Claude Code CLI integration**

## Overview

This guide transforms the SERP scanner from hardcoded mappings to dynamic, AI-powered query generation using Claude Code CLI. The hybrid approach maintains 100% reliability while adding unlimited scalability and intelligence.

## Architecture Philosophy

### Hybrid Intelligence Model
- **Speed First**: Simple/known inputs use hardcoded mappings (milliseconds)
- **AI Enhancement**: Complex/unknown inputs trigger Claude CLI (14-43 seconds)
- **Zero Downtime**: Graceful fallback ensures system always works
- **Smart Caching**: TTL-based caching minimizes API costs

### Decision Framework
Use **Hardcoded Mappings** when:
- Input matches known patterns (Jakarta, CEO, fintech, etc.)
- Performance is critical (< 1 second response required)
- API costs need to be minimized
- Network connectivity is unreliable

Use **AI Generation** when:
- Input contains unknown locations, industries, or seniority levels
- Complex combinations requiring contextual understanding
- Market-specific terminology or trends
- Quality is more important than speed

## Prompt Engineering Strategies

### Location Expansion Prompts

#### Base Template
```
Generate comprehensive LinkedIn location expansions for "[LOCATION]" in Indonesian business context.

Requirements:
- Include formal names (e.g., "DKI Jakarta" for Jakarta)
- Add regency/city variations (e.g., "Jakarta Pusat", "Jakarta Selatan")
- Include province-level names (e.g., "Jawa Timur" for Surabaya)
- Consider common expatriate spellings and variations
- Focus on business districts and commercial centers

Output Format:
{
  "location_mappings": "formatted search terms with OR operators",
  "coverage_assessment": "assessment of expansion completeness",
  "local_considerations": "Indonesian-specific business context notes"
}
```

#### Advanced Location Prompts
- **New Regions**: `"Generate location expansions for [REGION] including all major cities, regencies, and business districts"`
- **International**: `"Create location expansions for [COUNTRY] targeting Indonesian expatriates and international business hubs"`
- **Specific Districts**: `"Generate detailed location mappings for [DISTRICT] including all sub-districts and commercial areas"`

### Seniority Expansion Prompts

#### Base Template
```
Expand Indonesian business seniority level "[SENIORITY]" with all relevant titles and variations.

Requirements:
- Include English and Indonesian titles (CEO, "Direktur Utama")
- Add common variations and abbreviations (C-level, C-level Executive)
- Include functional equivalents (CTO, "Head of Technology", "Technology Director")
- Consider startup vs corporate terminology differences
- Include Indonesian-specific titles (Direktur, Komisaris, Manajer)

Output Format:
{
  "seniority_mappings": "comprehensive title expansions with OR operators",
  "context_notes": "industry-specific considerations",
  "indonesian_variants": "local language title variations"
}
```

#### Advanced Seniority Prompts
- **Industry-Specific**: `"Expand [SENIORITY] titles specifically for [INDUSTRY] sector in Indonesia"`
- **Startup Context**: `"Generate startup-appropriate founder and leadership titles for Indonesian tech companies"`
- **Government/State-Owned**: `"Create seniority mappings for BUMN and government-related positions"`

### Industry Expansion Prompts

#### Base Template
```
Generate comprehensive industry keywords for "[INDUSTRY]" in Indonesian market context.

Requirements:
- Include English and Indonesian terms (fintech, "teknologi finansial")
- Add related sub-sectors and verticals
- Include technology readiness indicators
- Consider market size and maturity
- Add common industry associations and certifications

Output Format:
{
  "industry_mappings": "comprehensive industry keywords with OR operators",
  "related_technologies": "associated technology stacks and platforms",
  "market_indicators": "signs of market maturity and adoption",
  "indonesian_context": "local market characteristics and regulations"
}
```

#### Advanced Industry Prompts
- **Emerging Technologies**: `"Generate keywords for [EMERGING_TECH] in Indonesian market, including adoption indicators"`
- **Traditional Industries**: `"Create modern digital transformation keywords for [TRADITIONAL_INDUSTRY] in Indonesia"`
- **Export-Focused**: `"Generate industry terms for Indonesian companies targeting international markets"`

### Technology Readiness Prompts

#### Base Template
```
Generate technology readiness indicators for "[TECHNOLOGY]" adoption in Indonesian businesses.

Requirements:
- Include infrastructure requirements and prerequisites
- Add implementation readiness signals
- Consider company size and maturity factors
- Include vendor and ecosystem keywords
- Add Indonesian-specific adoption challenges

Output Format:
{
  "technology_mappings": "readiness indicators with OR operators",
  "infrastructure_signals": "technical prerequisites and setup requirements",
  "adoption_indicators": "signs of successful implementation",
  "vendor_ecosystem": "related service providers and platforms"
}
```

## Schema Definitions

### Location Mapping Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "location_mappings": {
      "type": "string",
      "description": "LinkedIn search terms with OR operators",
      "pattern": "^[\\w\\s\"\\-\\(\\)OR]+$"
    },
    "coverage_assessment": {
      "type": "string",
      "description": "Assessment of expansion completeness"
    },
    "local_considerations": {
      "type": "string",
      "description": "Indonesian business context notes"
    }
  },
  "required": ["location_mappings"]
}
```

### Seniority Mapping Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "seniority_mappings": {
      "type": "string",
      "description": "Seniority title expansions with OR operators",
      "pattern": "^[\\w\\s\"\\-\\(\\)OR]+$"
    },
    "context_notes": {
      "type": "string",
      "description": "Industry-specific considerations"
    },
    "indonesian_variants": {
      "type": "string",
      "description": "Local language title variations"
    }
  },
  "required": ["seniority_mappings"]
}
```

### Industry Mapping Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "industry_mappings": {
      "type": "string",
      "description": "Industry keywords with OR operators",
      "pattern": "^[\\w\\s\"\\-\\(\\)OR]+$"
    },
    "related_technologies": {
      "type": "string",
      "description": "Associated technology stacks"
    },
    "market_indicators": {
      "type": "string",
      "description": "Market maturity signals"
    },
    "indonesian_context": {
      "type": "string",
      "description": "Local market characteristics"
    }
  },
  "required": ["industry_mappings"]
}
```

## Quality Validation Criteria

### Output Quality Standards
- **Comprehensiveness**: Minimum 3-5 terms per mapping component
- **Relevance**: All terms must be relevant to Indonesian LinkedIn profiles
- **Format Compliance**: Proper OR operator syntax and quotation mark usage
- **Context Awareness**: Terms appropriate for business/professional context
- **Cultural Sensitivity**: Respect Indonesian business culture and terminology

### Validation Checklists
#### Location Validation
- [ ] Includes major city variations (Jakarta, DKI Jakarta)
- [ ] Covers administrative divisions (provinces, regencies)
- [ ] Contains business district names
- [ ] Uses proper Indonesian spelling conventions
- [ ] Avoids overly broad geographic terms

#### Seniority Validation
- [ ] Covers both English and Indonesian titles
- [ ] Includes C-level and director-level equivalents
- [ ] Considers startup vs corporate differences
- [ ] Contains common abbreviations and variations
- [ ] Excludes inappropriate or junior-level titles

#### Industry Validation
- [ ] Includes both technical and business terms
- [ ] Covers emerging trends and established practices
- [ ] Contains relevant technology keywords
- [ ] Addresses Indonesian market specifics
- [ ] Avoids overly generic or unrelated terms

### Benchmarking Standards
AI-generated mappings must meet or exceed hardcoded mapping performance:
- **Result Count**: Generate comparable or higher lead volumes
- **Lead Quality**: Maintain or improve relevance scores
- **Query Precision**: Avoid overly broad or narrow searches
- **Cultural Fit**: Resonate with Indonesian business practices

## Performance Optimization Strategies

### Caching Strategy
```python
# Cache Configuration
CACHE_TTL = 3600  # 1 hour for location/seniority mappings
CACHE_TTL_INDUSTRY = 7200  # 2 hours for industry mappings
MAX_CACHE_SIZE = 1000  # Maximum cached mappings

# Cache Key Strategy
cache_key = f"{component_type}:{normalized_input}:{context_hash}"
```

### Intelligent Routing Rules
```python
def should_use_ai(components):
    # Use AI for unknown locations
    if not components['locations'] or any(loc not in KNOWN_LOCATIONS for loc in components['locations']):
        return True

    # Use AI for unknown industries
    if not components['industries'] or any(ind not in KNOWN_INDUSTRIES for ind in components['industries']):
        return True

    # Use AI for complex combinations (> 2 components)
    complexity_score = sum(len(components[key]) for key in components)
    if complexity_score > 2:
        return True

    return False
```

### Cost Management
- **Batch Processing**: Group multiple components in single API calls
- **Progressive Enhancement**: Start with hardcoded, upgrade with AI
- **Usage Monitoring**: Track API costs and set daily limits
- **Quality Thresholds**: Only use AI results meeting quality standards

## Error Handling and Fallback

### Fallback Strategy
1. **Primary**: Try AI generation with 60-second timeout
2. **Secondary**: Check cache for recent valid mappings
3. **Tertiary**: Use hardcoded mappings as final fallback
4. **Emergency**: Return basic query structure without advanced mappings

### Error Recovery
```python
def safe_generate_mappings(input_text):
    try:
        # Attempt AI generation
        ai_result = call_claude_cli(input_text)
        if validate_quality(ai_result):
            return ai_result
    except (TimeoutError, APIError):
        log_ai_failure(input_text)

    # Fallback to cached or hardcoded
    return get_fallback_mappings(input_text)
```

## Implementation Guidelines

### Claude CLI Integration
```bash
# Basic Command Structure
claude -p "PROMPT" --output-format json --json-schema schema.json

# Timeout Handling
timeout 60s claude -p "PROMPT" --output-format json

# Error Handling
if ! claude -p "PROMPT" --output-format json 2>/dev/null; then
    # Fallback to hardcoded
fi
```

### Python Integration
```python
import subprocess
import json
import asyncio
from datetime import datetime, timedelta

class AIQueryGenerator:
    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=3600)
        self.fallback = HardcodedMappings()

    async def generate_mappings(self, input_text):
        cache_key = f"query:{hash(input_text)}"

        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Try AI generation
        result = await self.call_claude_cli(input_text)
        if result and self.validate_quality(result):
            self.cache[cache_key] = result
            return result

        # Fallback to hardcoded
        return self.fallback.parse_input(input_text)
```

## Monitoring and Improvement

### Success Metrics
- **Query Quality**: Lead relevance and conversion rates
- **System Performance**: Response times and success rates
- **Cost Efficiency**: API usage optimization
- **User Satisfaction**: Same interface, better results

### Continuous Improvement
- **Feedback Loops**: Learn from successful query patterns
- **A/B Testing**: Compare AI vs hardcoded performance
- **Quality Monitoring**: Regular validation against benchmarks
- **Prompt Optimization**: Refine prompts based on results

## Migration Strategy

### Phase 1: Foundation (Week 1)
- Create guidelines.md documentation
- Implement basic Claude CLI integration
- Add comprehensive error handling

### Phase 2: Integration (Week 2)
- Modify query_builder.py with hybrid architecture
- Implement caching and fallback systems
- Add quality validation

### Phase 3: Optimization (Week 3)
- Fine-tune intelligent routing
- Optimize caching strategy
- Implement monitoring and metrics

### Phase 4: Migration (Week 4)
- Gradually increase AI usage
- Remove old mappings.md
- Full deployment with fallback support

## Best Practices

### Prompt Engineering
- Be specific about Indonesian context and requirements
- Include output format examples
- Set clear quality expectations
- Request confidence levels for suggestions

### Performance Optimization
- Cache frequently used mappings
- Use timeouts for API calls
- Implement graceful degradation
- Monitor API costs and usage

### Quality Assurance
- Validate all AI outputs before caching
- Maintain comprehensive fallback coverage
- Regular benchmark against hardcoded performance
- Collect user feedback for continuous improvement

This guidelines document provides the foundation for transforming the SERP scanner into an intelligent, adaptive lead generation platform while maintaining the reliability and performance users depend on.