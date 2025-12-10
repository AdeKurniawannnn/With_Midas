#!/usr/bin/env python3
"""
AI-Native Query Generator for SERP Scanner

Advanced AI-powered query generation using Claude Code CLI with complete
component extraction and query construction capabilities.
Replaces all hardcoded mappings with dynamic AI-driven processing.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import hashlib
import os
import re
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryQuality(Enum):
    """Query quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"


@dataclass
class CacheEntry:
    """Represents a cached mapping entry with TTL."""
    data: Dict[str, Any]
    timestamp: datetime
    ttl: timedelta
    quality_score: Optional[float] = None

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now() > (self.timestamp + self.ttl)


@dataclass
class QueryComponents:
    """Structured representation of extracted query components."""
    locations: List[Dict[str, str]]
    seniority: List[Dict[str, str]]
    industries: List[Dict[str, str]]
    technologies: List[Dict[str, str]]
    implicit_components: List[str]
    target_intent: Dict[str, Any]
    confidence_score: float
    extraction_metadata: Dict[str, Any]


@dataclass
class ConstructedQuery:
    """Complete constructed query with quality metrics."""
    query_string: str
    base_url: str
    search_terms: List[str]
    filters: List[str]
    exclusion_terms: List[str]
    quality_metrics: Dict[str, Union[float, str]]
    boolean_logic: Dict[str, Any]
    confidence_score: float
    construction_metadata: Dict[str, Any]


class TTLCache:
    """Enhanced TTL-based cache for AI-generated components and queries."""

    def __init__(self, max_size: int = 2000, default_ttl: timedelta = timedelta(hours=2)):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._hit_count = 0
        self._miss_count = 0

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if available and not expired."""
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                logger.debug(f"Cache hit for key: {key}")
                self._hit_count += 1
                return entry.data
            else:
                # Remove expired entry
                del self._cache[key]
                logger.debug(f"Cache expired for key: {key}")
        self._miss_count += 1
        return None

    def set(self, key: str, data: Dict[str, Any], ttl: Optional[timedelta] = None, quality_score: Optional[float] = None) -> None:
        """Cache data with TTL and quality score."""
        # Remove oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(),
                           key=lambda k: self._cache[k].timestamp)
            del self._cache[oldest_key]

        entry = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            ttl=ttl or self.default_ttl,
            quality_score=quality_score
        )
        self._cache[key] = entry
        logger.debug(f"Cached data for key: {key} (quality: {quality_score})")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total_requests * 100) if total_requests > 0 else 0

        return {
            "total_entries": len(self._cache),
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate_percent": round(hit_rate, 2),
            "max_size": self.max_size
        }

    def clear(self) -> None:
        """Clear all cache entries and reset statistics."""
        self._cache.clear()
        self._hit_count = 0
        self._miss_count = 0
        logger.debug("Cache cleared and statistics reset")


class AIQueryGenerator:
    """AI-native query generator with complete component extraction and query construction."""

    def __init__(self):
        self.cache = TTLCache(max_size=2000, default_ttl=timedelta(hours=2))

        # Enhanced directory structure
        self.script_dir = Path(__file__).parent
        self.skill_dir = self.script_dir.parent
        self.schema_dir = self.skill_dir / "schemas"
        self.prompts_dir = self.skill_dir / "prompts"

        # Ensure directories exist
        self.schema_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)

        # AI configuration
        self.ai_enabled = os.getenv('SERP_AI_ENABLED', 'true').lower() == 'true'
        self.ai_timeout = int(os.getenv('SERP_AI_TIMEOUT', '60'))
        self.max_retries = int(os.getenv('SERP_AI_MAX_RETRIES', '3'))

        # Quality thresholds
        self.min_confidence_threshold = float(os.getenv('SERP_MIN_CONFIDENCE', '0.7'))
        self.quality_threshold = float(os.getenv('SERP_QUALITY_THRESHOLD', '0.75'))

        # Performance tracking
        self.performance_metrics = {
            'extractions': 0,
            'constructions': 0,
            'cache_hits': 0,
            'ai_calls': 0,
            'fallbacks': 0,
            'errors': 0
        }

    def _get_cache_key(self, operation: str, input_data: str, context: str = "") -> str:
        """Generate cache key for AI operations."""
        key_data = f"{operation}:{input_data.lower()}:{context}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def _call_claude_cli_with_retry(self, prompt: str, schema_path: Optional[str] = None, operation_type: str = "generic") -> Optional[Dict[str, Any]]:
        """Call Claude CLI with enhanced error handling and retry logic."""
        if not self.ai_enabled:
            logger.warning("AI is disabled, skipping Claude CLI call")
            return None

        self.performance_metrics['ai_calls'] += 1

        for attempt in range(self.max_retries):
            try:
                cmd = ["claude", "-p", prompt]

                if schema_path and Path(schema_path).exists():
                    cmd.extend(["--json-schema", schema_path])
                else:
                    cmd.extend(["--output-format", "json"])

                # Execute Claude CLI with timeout
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                try:
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.ai_timeout)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    logger.error(f"Claude CLI call timed out (attempt {attempt + 1})")
                    if attempt == self.max_retries - 1:
                        self.performance_metrics['errors'] += 1
                    continue

                if process.returncode != 0:
                    logger.error(f"Claude CLI failed with return code {process.returncode} (attempt {attempt + 1})")
                    logger.error(f"STDERR: {stderr.decode()}")
                    if attempt == self.max_retries - 1:
                        self.performance_metrics['errors'] += 1
                    continue

                # Parse JSON response
                try:
                    result = json.loads(stdout.decode())
                    logger.debug(f"Claude CLI response received successfully for {operation_type}")
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Claude CLI JSON response: {e} (attempt {attempt + 1})")
                    if attempt == self.max_retries - 1:
                        self.performance_metrics['errors'] += 1
                    continue

            except Exception as e:
                logger.error(f"Error calling Claude CLI: {e} (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    self.performance_metrics['errors'] += 1
                continue

        logger.error(f"All Claude CLI attempts failed for {operation_type}")
        return None

    def create_component_extraction_prompt(self, input_text: str) -> str:
        """Create structured prompt for component extraction."""
        prompt_path = self.prompts_dir / "component_extraction.yaml"

        if prompt_path.exists():
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
                return prompt_template.replace("{{INPUT_TEXT}}", input_text)
            except Exception as e:
                logger.warning(f"Failed to load prompt template: {e}")

        # Fallback prompt
        return f"""
Extract structured components for LinkedIn executive search from: "{input_text}"

CONTEXT: Indonesian B2B lead generation targeting executives and decision-makers.

REQUIREMENTS:
1. Extract locations with Indonesian geographic context (Jakarta, Surabaya, etc.)
2. Identify seniority levels and executive titles (CEO, CTO, Director, etc.)
3. Recognize industries and sectors (fintech, cloud, AI, manufacturing, etc.)
4. Identify technology readiness and company types (startup, enterprise, cloud, etc.)
5. Capture implicit requirements and target intent

OUTPUT JSON FORMAT:
{{
  "locations": [{{"city": "...", "region": "...", "country": "..."}}],
  "seniority": [{{"level": "...", "title_variants": ["..."]}}],
  "industries": [{{"primary": "...", "secondary": ["..."]}}],
  "technologies": [{{"readiness": "...", "company_types": ["..."]}}],
  "implicit_components": ["..."],
  "target_intent": {{ "strategy": "...", "focus": "..." }},
  "confidence_score": 0.0-1.0,
  "extraction_metadata": {{ "complexity": "...", "ambiguity": "..." }}
}}

Focus on Indonesian business context and executive-level targeting.
"""

    def create_query_construction_prompt(self, components: QueryComponents) -> str:
        """Create structured prompt for query construction."""
        prompt_path = self.prompts_dir / "query_construction.yaml"

        if prompt_path.exists():
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
                return prompt_template.replace("{{COMPONENTS}}", json.dumps(components.__dict__, indent=2))
            except Exception as e:
                logger.warning(f"Failed to load prompt template: {e}")

        # Fallback prompt
        return f"""
Construct optimized LinkedIn search query from extracted components.

COMPONENTS:
{json.dumps(components.__dict__, indent=2)}

REQUIREMENTS:
1. Build query with proper Boolean logic and operator precedence
2. Use exact match operators with strategic quotation mark placement
3. Generate context-appropriate exclusion filters
4. Optimize for precision and coverage
5. Apply LinkedIn search best practices
6. Consider Indonesian business context and geographic targeting

OUTPUT JSON FORMAT:
{{
  "query_structure": {{
    "base_url": "site:linkedin.com/in",
    "search_terms": ["..."],
    "filters": ["..."],
    "boolean_logic": {{"operators": ["AND", "OR"], "precedence": "..."}}
  }},
  "exact_match": {{"terms": ["..."], "strategy": "..."}},
  "exclusion_filters": ["..."],
  "quality_metrics": {{
    "precision_score": 0.0-1.0,
    "coverage_score": 0.0-1.0,
    "complexity_score": 0.0-1.0,
    "optimization_notes": "..."
  }},
  "confidence_score": 0.0-1.0,
  "construction_metadata": {{
    "query_length": "...",
    "optimization_level": "...",
    "target_specificity": "..."
  }}
}}

Focus on executive-level targeting and Indonesian market optimization.
"""

    async def extract_components(self, input_text: str) -> QueryComponents:
        """Extract components using AI-powered natural language processing."""
        self.performance_metrics['extractions'] += 1

        # Check cache first
        cache_key = self._get_cache_key("extract_components", input_text)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.performance_metrics['cache_hits'] += 1
            logger.debug("Using cached component extraction")
            return QueryComponents(**cached_result)

        # Generate prompt
        prompt = self.create_component_extraction_prompt(input_text)
        schema_path = self.schema_dir / "component_extraction.json"

        # Call AI with schema validation
        result = await self._call_claude_cli_with_retry(prompt, str(schema_path), "component_extraction")

        if result and self._validate_component_extraction(result):
            components = QueryComponents(
                locations=result.get("locations", []),
                seniority=result.get("seniority", []),
                industries=result.get("industries", []),
                technologies=result.get("technologies", []),
                implicit_components=result.get("implicit_components", []),
                target_intent=result.get("target_intent", {}),
                confidence_score=result.get("confidence_score", 0.0),
                extraction_metadata=result.get("extraction_metadata", {})
            )

            # Cache successful extraction
            cache_data = {
                "locations": components.locations,
                "seniority": components.seniority,
                "industries": components.industries,
                "technologies": components.technologies,
                "implicit_components": components.implicit_components,
                "target_intent": components.target_intent,
                "confidence_score": components.confidence_score,
                "extraction_metadata": components.extraction_metadata
            }
            self.cache.set(cache_key, cache_data, ttl=timedelta(hours=4), quality_score=components.confidence_score)

            logger.info(f"Component extraction completed with confidence: {components.confidence_score:.2f}")
            return components
        else:
            # Fallback to basic extraction
            self.performance_metrics['fallbacks'] += 1
            logger.warning("AI component extraction failed, using fallback")
            return self._fallback_component_extraction(input_text)

    def _validate_component_extraction(self, result: Dict[str, Any]) -> bool:
        """Validate component extraction results meet quality standards."""
        if not isinstance(result, dict):
            return False

        # Check for required fields
        required_fields = ["locations", "seniority", "industries", "technologies", "confidence_score"]
        if not all(field in result for field in required_fields):
            logger.error("Missing required fields in component extraction")
            return False

        # Validate confidence score
        confidence = result.get("confidence_score", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            logger.error(f"Invalid confidence score: {confidence}")
            return False

        # Check minimum confidence threshold
        if confidence < self.min_confidence_threshold:
            logger.warning(f"Low confidence score: {confidence}")
            # Still allow but log warning

        return True

    def _fallback_component_extraction(self, input_text: str) -> QueryComponents:
        """Fallback component extraction using basic pattern matching."""
        input_lower = input_text.lower()

        # Basic keyword extraction
        location_keywords = ["jakarta", "surabaya", "bandung", "bali", "medan", "indonesia", "jawa", "sumatra", "kalimantan", "sulawesi"]
        seniority_keywords = ["ceo", "cto", "cio", "cfo", "coo", "director", "vp", "head", "manager", "founder", "president", "komisaris", "direktur"]
        industry_keywords = ["fintech", "cloud", "ai", "manufacturing", "ecommerce", "banking", "insurance", "telecom", "retail", "healthcare", "education", "logistik"]
        tech_keywords = ["cloud", "startup", "enterprise", "digital", "mobile", "web", "data", "security", "infrastructure", "devops"]

        locations = [{"city": kw, "region": "", "country": "Indonesia"} for kw in location_keywords if kw in input_lower]
        seniority = [{"level": kw, "title_variants": [kw.title()]} for kw in seniority_keywords if kw in input_lower]
        industries = [{"primary": kw, "secondary": []} for kw in industry_keywords if kw in input_lower]
        technologies = [{"readiness": kw, "company_types": []} for kw in tech_keywords if kw in input_lower]

        return QueryComponents(
            locations=locations,
            seniority=seniority,
            industries=industries,
            technologies=technologies,
            implicit_components=[],
            target_intent={"strategy": "lead_generation", "focus": "executive_level"},
            confidence_score=0.3,  # Low confidence for fallback
            extraction_metadata={"method": "fallback_pattern_matching", "complexity": "basic"}
        )

    async def build_complete_query(self, components: QueryComponents) -> ConstructedQuery:
        """Build complete query using AI-powered construction from extracted components."""
        self.performance_metrics['constructions'] += 1

        # Check cache first
        components_str = json.dumps(components.__dict__, sort_keys=True)
        cache_key = self._get_cache_key("build_query", components_str)
        cached_result = self.cache.get(cache_key)
        if cached_result:
            self.performance_metrics['cache_hits'] += 1
            logger.debug("Using cached query construction")
            return ConstructedQuery(**cached_result)

        # Generate prompt
        prompt = self.create_query_construction_prompt(components)
        schema_path = self.schema_dir / "query_construction.json"

        # Call AI with schema validation
        result = await self._call_claude_cli_with_retry(prompt, str(schema_path), "query_construction")

        if result and self._validate_query_construction(result):
            # Extract query structure
            query_structure = result.get("query_structure", {})
            quality_metrics = result.get("quality_metrics", {})
            exact_match = result.get("exact_match", {})

            # Build final query string
            query_parts = [query_structure.get("base_url", "site:linkedin.com/in")]

            # Add search terms with Boolean logic
            search_terms = query_structure.get("search_terms", [])
            if search_terms:
                query_parts.extend(search_terms)

            # Add filters
            filters = query_structure.get("filters", [])
            if filters:
                query_parts.extend(filters)

            # Add exclusion filters
            exclusion_filters = result.get("exclusion_filters", [])
            if exclusion_filters:
                query_parts.extend([f"-{ef}" for ef in exclusion_filters])

            query_string = ' '.join(query_parts)

            constructed_query = ConstructedQuery(
                query_string=query_string,
                base_url=query_structure.get("base_url", "site:linkedin.com/in"),
                search_terms=search_terms,
                filters=filters,
                exclusion_terms=exclusion_filters,
                quality_metrics=quality_metrics,
                boolean_logic=query_structure.get("boolean_logic", {}),
                confidence_score=result.get("confidence_score", 0.0),
                construction_metadata=result.get("construction_metadata", {})
            )

            # Cache successful construction
            cache_data = {
                "query_string": constructed_query.query_string,
                "base_url": constructed_query.base_url,
                "search_terms": constructed_query.search_terms,
                "filters": constructed_query.filters,
                "exclusion_terms": constructed_query.exclusion_terms,
                "quality_metrics": constructed_query.quality_metrics,
                "boolean_logic": constructed_query.boolean_logic,
                "confidence_score": constructed_query.confidence_score,
                "construction_metadata": constructed_query.construction_metadata
            }
            self.cache.set(cache_key, cache_data, ttl=timedelta(hours=6), quality_score=constructed_query.confidence_score)

            logger.info(f"Query construction completed with confidence: {constructed_query.confidence_score:.2f}")
            return constructed_query
        else:
            # Fallback to basic query construction
            self.performance_metrics['fallbacks'] += 1
            logger.warning("AI query construction failed, using fallback")
            return self._fallback_query_construction(components)

    def _validate_query_construction(self, result: Dict[str, Any]) -> bool:
        """Validate query construction results meet quality standards."""
        if not isinstance(result, dict):
            return False

        # Check for required fields
        required_fields = ["query_structure", "quality_metrics", "confidence_score"]
        if not all(field in result for field in required_fields):
            logger.error("Missing required fields in query construction")
            return False

        # Validate confidence score
        confidence = result.get("confidence_score", 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            logger.error(f"Invalid confidence score: {confidence}")
            return False

        # Validate quality metrics
        quality_metrics = result.get("quality_metrics", {})
        required_quality_fields = ["precision_score", "coverage_score"]
        if not all(field in quality_metrics for field in required_quality_fields):
            logger.error("Missing required quality metric fields")
            return False

        # Check minimum quality threshold
        precision = quality_metrics.get("precision_score", 0)
        coverage = quality_metrics.get("coverage_score", 0)
        if precision < self.quality_threshold or coverage < self.quality_threshold:
            logger.warning(f"Low quality scores - precision: {precision}, coverage: {coverage}")
            # Still allow but log warning

        return True

    def _fallback_query_construction(self, components: QueryComponents) -> ConstructedQuery:
        """Fallback query construction using basic Boolean logic."""
        query_parts = ['site:linkedin.com/in']

        # Process locations
        if components.locations:
            location_terms = []
            for loc in components.locations:
                city = loc.get("city", "")
                region = loc.get("region", "")
                if city and region:
                    location_terms.append(f'"{city}" OR "{region}"')
                elif city:
                    location_terms.append(f'"{city}"')
            if location_terms:
                query_parts.append(f"({' OR '.join(location_terms)})")

        # Process seniority
        if components.seniority:
            seniority_terms = []
            for sen in components.seniority:
                level = sen.get("level", "")
                variants = sen.get("title_variants", [])
                if level:
                    all_terms = [level.title()] + variants
                    seniority_terms.append(' OR '.join([f'"{t}"' for t in all_terms]))
            if seniority_terms:
                query_parts.append(f"({' OR '.join(seniority_terms)})")

        # Process industries
        if components.industries:
            industry_terms = []
            for ind in components.industries:
                primary = ind.get("primary", "")
                secondary = ind.get("secondary", [])
                if primary:
                    all_terms = [primary.lower()] + [s.lower() for s in secondary]
                    industry_terms.append(' OR '.join(all_terms))
            if industry_terms:
                query_parts.append(f"({' OR '.join(industry_terms)})")

        # Process technologies
        if components.technologies:
            tech_terms = []
            for tech in components.technologies:
                readiness = tech.get("readiness", "")
                if readiness:
                    tech_terms.append(readiness.lower())
            if tech_terms:
                query_parts.append(f"({' OR '.join(tech_terms)})")

        # Add standard exclusion filters
        query_parts.append('-recruiter -hr -human -resources -intern -student -graduate -trainer -consultant -freelance')

        query_string = ' '.join(query_parts)

        return ConstructedQuery(
            query_string=query_string,
            base_url="site:linkedin.com/in",
            search_terms=[term for term in query_parts[1:-1] if not term.startswith('-')],
            filters=[],
            exclusion_filters=[term[1:] for term in query_parts if term.startswith('-')],
            quality_metrics={
                "precision_score": 0.5,
                "coverage_score": 0.6,
                "complexity_score": 0.4,
                "optimization_notes": "Basic fallback construction"
            },
            boolean_logic={"operators": ["AND", "OR"], "precedence": "standard"},
            confidence_score=0.4,  # Low confidence for fallback
            construction_metadata={
                "method": "fallback_boolean_logic",
                "query_length": str(len(query_string)),
                "optimization_level": "basic",
                "target_specificity": "low"
            }
        )

    async def generate_exclusion_terms(self, components: QueryComponents, context: str = "") -> List[str]:
        """Generate intelligent exclusion terms based on context and components."""
        cache_key = self._get_cache_key("exclusion_terms", context or "general", json.dumps(components.__dict__))
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result.get("exclusion_terms", [])

        # Standard exclusion terms for executive searches
        base_exclusions = [
            "recruiter", "hr", "human", "resources", "intern", "student",
            "graduate", "trainer", "consultant", "freelance", "volunteer",
            "internship", "trainee", "junior"
        ]

        # Context-specific exclusions
        if components.seniority:
            # For executive searches, exclude more junior terms
            base_exclusions.extend(["junior", "entry", "associate", "assistant", "coordinator"])

        if components.industries:
            # Industry-specific exclusions
            for industry in components.industries:
                primary = industry.get("primary", "").lower()
                if "tech" in primary or "software" in primary:
                    base_exclusions.extend(["developer", "programmer", "coder"])

        result = {"exclusion_terms": base_exclusions}
        self.cache.set(cache_key, result, ttl=timedelta(hours=24))
        return base_exclusions

    def validate_query_quality(self, query: ConstructedQuery) -> QueryQuality:
        """Validate and assess the quality of constructed queries."""
        if not query or not query.query_string:
            return QueryQuality.POOR

        quality_score = query.confidence_score
        precision_score = query.quality_metrics.get("precision_score", 0)
        coverage_score = query.quality_metrics.get("coverage_score", 0)

        # Calculate overall quality score
        overall_score = (quality_score + precision_score + coverage_score) / 3

        if overall_score >= 0.9:
            return QueryQuality.EXCELLENT
        elif overall_score >= 0.75:
            return QueryQuality.GOOD
        elif overall_score >= 0.5:
            return QueryQuality.ACCEPTABLE
        else:
            return QueryQuality.POOR

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        cache_stats = self.cache.get_cache_stats()

        metrics = {
            "operations": self.performance_metrics.copy(),
            "cache_performance": cache_stats,
            "ai_enabled": self.ai_enabled,
            "configuration": {
                "timeout": self.ai_timeout,
                "max_retries": self.max_retries,
                "min_confidence_threshold": self.min_confidence_threshold,
                "quality_threshold": self.quality_threshold
            }
        }

        # Calculate success rates
        total_operations = sum(self.performance_metrics['extractions'], self.performance_metrics['constructions'])
        if total_operations > 0:
            fallback_rate = self.performance_metrics['fallbacks'] / total_operations * 100
            error_rate = self.performance_metrics['errors'] / total_operations * 100

            metrics["success_rates"] = {
                "fallback_rate_percent": round(fallback_rate, 2),
                "error_rate_percent": round(error_rate, 2),
                "success_rate_percent": round(100 - fallback_rate - error_rate, 2)
            }

        return metrics

    async def process_natural_language_query(self, input_text: str) -> ConstructedQuery:
        """Complete end-to-end processing from natural language to constructed query."""
        logger.info(f"Processing natural language query: '{input_text}'")

        # Step 1: Extract components
        components = await self.extract_components(input_text)
        logger.info(f"Extracted components confidence: {components.confidence_score:.2f}")

        # Step 2: Build complete query
        constructed_query = await self.build_complete_query(components)
        logger.info(f"Constructed query confidence: {constructed_query.confidence_score:.2f}")

        # Step 3: Validate quality
        quality = self.validate_query_quality(constructed_query)
        logger.info(f"Query quality assessment: {quality.value}")

        return constructed_query


# Utility functions for backward compatibility
async def parse_components(input_text: str) -> Dict[str, List[str]]:
    """AI-powered component extraction for backward compatibility."""
    ai_generator = AIQueryGenerator()
    components = await ai_generator.extract_components(input_text)

    # Convert to legacy format
    return {
        "locations": [loc.get("city", "") for loc in components.locations if loc.get("city")],
        "seniority": [sen.get("level", "") for sen in components.seniority if sen.get("level")],
        "industries": [ind.get("primary", "") for ind in components.industries if ind.get("primary")],
        "technologies": [tech.get("readiness", "") for tech in components.technologies if tech.get("readiness")]
    }


async def build_query_from_mappings(mappings: Dict[str, Dict[str, str]]) -> str:
    """Build final query string from legacy mappings."""
    query_parts = ['site:linkedin.com/in']

    # Add location component
    if mappings.get('locations'):
        location_terms = list(mappings['locations'].values())
        if location_terms:
            query_parts.append(f"({' OR '.join(location_terms)})")

    # Add seniority component
    if mappings.get('seniority'):
        seniority_terms = list(mappings['seniority'].values())
        if seniority_terms:
            query_parts.append(f"({' OR '.join(seniority_terms)})")

    # Add industry component
    if mappings.get('industries'):
        industry_terms = list(mappings['industries'].values())
        if industry_terms:
            query_parts.append(f"({' OR '.join(industry_terms)})")

    # Add technology component
    if mappings.get('technologies'):
        tech_terms = list(mappings['technologies'].values())
        if tech_terms:
            query_parts.append(f"({' OR '.join(tech_terms)})")

    # Add standard exclusion filters
    query_parts.append('-recruiter -hr -human -resources -intern -student -graduate -trainer -consultant -freelance')

    return ' '.join(query_parts)


# Main execution function for testing
async def main():
    """Main function for testing AI-native query generation."""
    if len(sys.argv) < 2:
        print("Usage: python ai_query_generator.py '<natural language query>'")
        sys.exit(1)

    input_text = ' '.join(sys.argv[1:])
    print(f"Processing: {input_text}")
    print("=" * 50)

    ai_generator = AIQueryGenerator()

    try:
        # Process the query
        result = await ai_generator.process_natural_language_query(input_text)

        print(f"Generated Query: {result.query_string}")
        print(f"Confidence Score: {result.confidence_score:.2f}")
        print(f"Quality Assessment: {ai_generator.validate_query_quality(result).value}")

        # Show quality metrics
        if result.quality_metrics:
            print("\nQuality Metrics:")
            for metric, value in result.quality_metrics.items():
                print(f"  {metric}: {value}")

        # Show performance stats
        print("\nPerformance Stats:")
        stats = ai_generator.get_performance_metrics()
        print(f"  Cache Hit Rate: {stats['cache_performance']['hit_rate_percent']:.1f}%")
        print(f"  AI Calls: {stats['operations']['ai_calls']}")
        print(f"  Fallbacks: {stats['operations']['fallbacks']}")

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())