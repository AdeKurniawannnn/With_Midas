#!/usr/bin/env python3
"""
AI Quality Testing Framework for SERP Scanner
Comprehensive testing suite for AI-native query generation system.
"""

import asyncio
import json
import logging
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import statistics
import traceback

# Import the AI generator
from ai_query_generator import AIQueryGenerator, QueryQuality, QueryComponents, ConstructedQuery

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_ai_quality.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Individual test result with comprehensive metrics."""
    test_name: str
    input_text: str
    expected_output: Optional[str]
    actual_output: str
    confidence_score: float
    quality_assessment: QueryQuality
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    performance_data: Optional[Dict[str, Any]] = None


@dataclass
class BenchmarkResult:
    """Benchmark comparison between AI-only and previous systems."""
    test_category: str
    ai_only_results: List[TestResult]
    baseline_results: Optional[List[TestResult]] = None
    performance_improvement: Optional[float] = None
    quality_improvement: Optional[float] = None


class AIQualityTester:
    """Comprehensive testing framework for AI query generation quality."""

    def __init__(self):
        self.test_data = self._load_test_dataset()
        self.benchmark_data = self._load_benchmark_dataset()
        self.results_cache = {}
        self.test_reports = []

    def _load_test_dataset(self) -> List[Dict[str, Any]]:
        """Load comprehensive test dataset with expected outputs."""
        return [
            {
                "input": "CEO fintech Jakarta",
                "category": "basic_executive",
                "expected_query_elements": ["CEO", "Jakarta", "fintech"],
                "expected_confidence_min": 0.8,
                "expected_quality": QueryQuality.GOOD,
                "complexity": "low"
            },
            {
                "input": "CTO cloud startup Surabaya",
                "category": "technology_focus",
                "expected_query_elements": ["CTO", "cloud", "startup", "Surabaya"],
                "expected_confidence_min": 0.7,
                "expected_quality": QueryQuality.GOOD,
                "complexity": "medium"
            },
            {
                "input": "Looking for senior executives in Indonesian banking sector",
                "category": "complex_request",
                "expected_query_elements": ["executive", "banking", "Indonesia"],
                "expected_confidence_min": 0.6,
                "expected_quality": QueryQuality.ACCEPTABLE,
                "complexity": "high"
            },
            {
                "input": "Director manufacturing Medan with cloud experience",
                "category": "multi_component",
                "expected_query_elements": ["Director", "manufacturing", "Medan", "cloud"],
                "expected_confidence_min": 0.7,
                "expected_quality": QueryQuality.GOOD,
                "complexity": "medium"
            },
            {
                "input": "AI company founders in Bali",
                "category": "startup_focus",
                "expected_query_elements": ["founder", "AI", "Bali"],
                "expected_confidence_min": 0.6,
                "expected_quality": QueryQuality.ACCEPTABLE,
                "complexity": "medium"
            },
            {
                "input": "VP Technology enterprise Jakarta Selatan",
                "category": "senior_technical",
                "expected_query_elements": ["VP", "Technology", "enterprise", "Jakarta Selatan"],
                "expected_confidence_min": 0.7,
                "expected_quality": QueryQuality.GOOD,
                "complexity": "medium"
            },
            {
                "input": "Healthcare executives with digital transformation experience",
                "category": "industry_transformation",
                "expected_query_elements": ["executive", "healthcare", "digital", "transformation"],
                "expected_confidence_min": 0.5,
                "expected_quality": QueryQuality.ACCEPTABLE,
                "complexity": "high"
            },
            {
                "input": "Komisaris fintech dengan pengalaman cloud",
                "category": "local_language",
                "expected_query_elements": ["Komisaris", "fintech", "cloud"],
                "expected_confidence_min": 0.6,
                "expected_quality": QueryQuality.ACCEPTABLE,
                "complexity": "medium"
            },
            {
                "input": "CFO public company manufacturing Bandung",
                "category": "financial_executive",
                "expected_query_elements": ["CFO", "public", "manufacturing", "Bandung"],
                "expected_confidence_min": 0.7,
                "expected_quality": QueryQuality.GOOD,
                "complexity": "medium"
            },
            {
                "input": "Young entrepreneurs in e-commerce with mobile app experience",
                "category": "startup_mobile",
                "expected_query_elements": ["entrepreneur", "e-commerce", "mobile", "app"],
                "expected_confidence_min": 0.5,
                "expected_quality": QueryQuality.ACCEPTABLE,
                "complexity": "high"
            }
        ]

    def _load_benchmark_dataset(self) -> List[Dict[str, Any]]:
        """Load benchmark dataset for comparison testing."""
        return [
            {
                "input": "CEO Jakarta fintech",
                "baseline_query": 'site:linkedin.com/in ("Jakarta" OR "DKI Jakarta") (CEO OR "Chief Executive Officer" OR Founder) (fintech OR "financial technology") -recruiter -hr',
                "category": "executive_location_industry"
            },
            {
                "input": "CTO startup cloud",
                "baseline_query": 'site:linkedin.com/in (CTO OR "Chief Technology Officer") (startup OR entrepreneur) ("cloud computing" OR AWS OR Azure) -recruiter -developer',
                "category": "technical_startup"
            }
        ]

    async def run_component_extraction_tests(self, ai_generator: AIQueryGenerator) -> List[TestResult]:
        """Test component extraction accuracy and quality."""
        logger.info("Running component extraction tests...")
        results = []

        for test_case in self.test_data:
            try:
                start_time = time.time()

                # Extract components
                components = await ai_generator.extract_components(test_case["input"])
                execution_time = time.time() - start_time

                # Validate components contain expected elements
                success = self._validate_component_extraction(components, test_case)

                result = TestResult(
                    test_name=f"component_extraction_{test_case['category']}",
                    input_text=test_case["input"],
                    expected_output=str(test_case["expected_query_elements"]),
                    actual_output=str(components.__dict__),
                    confidence_score=components.confidence_score,
                    quality_assessment=QueryQuality.GOOD if components.confidence_score >= 0.7 else QueryQuality.ACCEPTABLE,
                    execution_time=execution_time,
                    success=success,
                    quality_metrics={
                        "components_count": len(components.locations) + len(components.seniority) + len(components.industries) + len(components.technologies),
                        "has_locations": len(components.locations) > 0,
                        "has_seniority": len(components.seniority) > 0,
                        "has_industries": len(components.industries) > 0,
                        "has_technologies": len(components.technologies) > 0
                    }
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Component extraction test failed for '{test_case['input']}': {e}")
                results.append(TestResult(
                    test_name=f"component_extraction_{test_case['category']}",
                    input_text=test_case["input"],
                    expected_output=str(test_case["expected_query_elements"]),
                    actual_output="",
                    confidence_score=0.0,
                    quality_assessment=QueryQuality.POOR,
                    execution_time=0.0,
                    success=False,
                    error_message=str(e)
                ))

        return results

    async def run_query_construction_tests(self, ai_generator: AIQueryGenerator) -> List[TestResult]:
        """Test complete query construction from natural language."""
        logger.info("Running query construction tests...")
        results = []

        for test_case in self.test_data:
            try:
                start_time = time.time()

                # Process complete query
                constructed_query = await ai_generator.process_natural_language_query(test_case["input"])
                execution_time = time.time() - start_time

                # Validate query quality
                quality = ai_generator.validate_query_quality(constructed_query)
                success = self._validate_query_construction(constructed_query, test_case)

                result = TestResult(
                    test_name=f"query_construction_{test_case['category']}",
                    input_text=test_case["input"],
                    expected_output=None,
                    actual_output=constructed_query.query_string,
                    confidence_score=constructed_query.confidence_score,
                    quality_assessment=quality,
                    execution_time=execution_time,
                    success=success,
                    quality_metrics=constructed_query.quality_metrics,
                    performance_data={
                        "query_length": len(constructed_query.query_string),
                        "search_terms_count": len(constructed_query.search_terms),
                        "exclusion_terms_count": len(constructed_query.exclusion_terms),
                        "has_boolean_logic": bool(constructed_query.boolean_logic)
                    }
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Query construction test failed for '{test_case['input']}': {e}")
                results.append(TestResult(
                    test_name=f"query_construction_{test_case['category']}",
                    input_text=test_case["input"],
                    expected_output=None,
                    actual_output="",
                    confidence_score=0.0,
                    quality_assessment=QueryQuality.POOR,
                    execution_time=0.0,
                    success=False,
                    error_message=str(e)
                ))

        return results

    async def run_performance_tests(self, ai_generator: AIQueryGenerator) -> List[TestResult]:
        """Test system performance under various load conditions."""
        logger.info("Running performance tests...")
        results = []

        # Test cache effectiveness
        cache_test_cases = ["CEO fintech Jakarta"] * 3  # Repeat for cache testing
        cache_times = []

        for i, test_input in enumerate(cache_test_cases):
            try:
                start_time = time.time()
                await ai_generator.process_natural_language_query(test_input)
                execution_time = time.time() - start_time
                cache_times.append(execution_time)

                if i == 0:
                    # First call should be slower (cache miss)
                    expected_time_range = (1.0, float('inf'))  # Should be >1 second
                else:
                    # Subsequent calls should be faster (cache hit)
                    expected_time_range = (0.0, 0.5)  # Should be <0.5 seconds

                success = expected_time_range[0] <= execution_time <= expected_time_range[1]

                results.append(TestResult(
                    test_name=f"performance_cache_{i+1}",
                    input_text=test_input,
                    expected_output=f"Time in range {expected_time_range}s",
                    actual_output=f"{execution_time:.3f}s",
                    confidence_score=1.0,
                    quality_assessment=QueryQuality.GOOD if success else QueryQuality.ACCEPTABLE,
                    execution_time=execution_time,
                    success=success
                ))

            except Exception as e:
                logger.error(f"Performance test failed: {e}")
                results.append(TestResult(
                    test_name=f"performance_cache_{i+1}",
                    input_text=test_input,
                    expected_output="Fast execution",
                    actual_output="Error",
                    confidence_score=0.0,
                    quality_assessment=QueryQuality.POOR,
                    execution_time=0.0,
                    success=False,
                    error_message=str(e)
                ))

        # Test concurrent processing
        try:
            start_time = time.time()
            concurrent_tasks = [
                ai_generator.process_natural_language_query("CEO fintech Jakarta"),
                ai_generator.process_natural_language_query("CTO cloud Surabaya"),
                ai_generator.process_natural_language_query("Director manufacturing Bandung")
            ]
            await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            total_time = time.time() - start_time

            results.append(TestResult(
                test_name="performance_concurrent",
                input_text="3 concurrent queries",
                expected_output="<5 seconds total",
                actual_output=f"{total_time:.3f}s total",
                confidence_score=1.0,
                quality_assessment=QueryQuality.GOOD if total_time < 5.0 else QueryQuality.ACCEPTABLE,
                execution_time=total_time,
                success=total_time < 5.0
            ))

        except Exception as e:
            logger.error(f"Concurrent performance test failed: {e}")
            results.append(TestResult(
                test_name="performance_concurrent",
                input_text="3 concurrent queries",
                expected_output="Fast concurrent execution",
                actual_output="Error",
                confidence_score=0.0,
                quality_assessment=QueryQuality.POOR,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            ))

        return results

    async def run_integration_tests(self, ai_generator: AIQueryGenerator) -> List[TestResult]:
        """Test end-to-end integration workflow."""
        logger.info("Running integration tests...")
        results = []

        # Test complete workflow with different input complexities
        integration_test_cases = [
            ("Simple executive search", "CEO Jakarta fintech", "simple_executive"),
            ("Multi-component search", "Director cloud manufacturing Bandung", "multi_component"),
            ("Natural language query", "Looking for senior executives in Indonesian tech companies", "natural_language"),
            ("Local language elements", "Komisaris startup fintek Jakarta", "local_language")
        ]

        for description, test_input, category in integration_test_cases:
            try:
                start_time = time.time()

                # Complete end-to-end processing
                result = await ai_generator.process_natural_language_query(test_input)
                execution_time = time.time() - start_time

                # Validate integration requirements
                integration_success = (
                    result.query_string.startswith("site:linkedin.com/in") and
                    result.confidence_score > 0.0 and
                    len(result.query_string) > 20 and
                    len(result.exclusion_terms) > 0
                )

                results.append(TestResult(
                    test_name=f"integration_{category}",
                    input_text=test_input,
                    expected_output="Valid LinkedIn query with exclusions",
                    actual_output=result.query_string,
                    confidence_score=result.confidence_score,
                    quality_assessment=ai_generator.validate_query_quality(result),
                    execution_time=execution_time,
                    success=integration_success,
                    performance_data={
                        "query_valid": result.query_string.startswith("site:linkedin.com/in"),
                        "has_exclusions": len(result.exclusion_terms) > 0,
                        "reasonable_length": 20 < len(result.query_string) < 2000
                    }
                ))

            except Exception as e:
                logger.error(f"Integration test failed for '{test_input}': {e}")
                results.append(TestResult(
                    test_name=f"integration_{category}",
                    input_text=test_input,
                    expected_output="Successful end-to-end processing",
                    actual_output="Integration Error",
                    confidence_score=0.0,
                    quality_assessment=QueryQuality.POOR,
                    execution_time=0.0,
                    success=False,
                    error_message=str(e)
                ))

        return results

    async def run_benchmark_comparison(self, ai_generator: AIQueryGenerator) -> List[BenchmarkResult]:
        """Run benchmark comparison with previous hardcoded system."""
        logger.info("Running benchmark comparison...")
        benchmark_results = []

        for category in ["executive_location_industry", "technical_startup"]:
            category_tests = [t for t in self.benchmark_data if t["category"] == category]
            ai_results = []

            for test_case in category_tests:
                try:
                    start_time = time.time()
                    ai_result = await ai_generator.process_natural_language_query(test_case["input"])
                    execution_time = time.time() - start_time

                    ai_results.append(TestResult(
                        test_name=f"ai_benchmark_{category}",
                        input_text=test_case["input"],
                        expected_output=test_case["baseline_query"],
                        actual_output=ai_result.query_string,
                        confidence_score=ai_result.confidence_score,
                        quality_assessment=ai_generator.validate_query_quality(ai_result),
                        execution_time=execution_time,
                        success=True,
                        quality_metrics=ai_result.quality_metrics
                    ))

                except Exception as e:
                    logger.error(f"Benchmark test failed: {e}")

            benchmark_results.append(BenchmarkResult(
                test_category=category,
                ai_only_results=ai_results,
                baseline_results=None  # Could be loaded from previous system results
            ))

        return benchmark_results

    def _validate_component_extraction(self, components: QueryComponents, test_case: Dict[str, Any]) -> bool:
        """Validate component extraction meets test requirements."""
        expected_elements = test_case["expected_query_elements"]
        min_confidence = test_case["expected_confidence_min"]

        # Check confidence threshold
        if components.confidence_score < min_confidence:
            return False

        # Check expected elements are present in components
        component_text = json.dumps(components.__dict__).lower()
        for element in expected_elements:
            if element.lower() not in component_text:
                logger.warning(f"Expected element '{element}' not found in extracted components")
                return False

        return True

    def _validate_query_construction(self, query: ConstructedQuery, test_case: Dict[str, Any]) -> bool:
        """Validate query construction meets test requirements."""
        min_confidence = test_case["expected_confidence_min"]
        expected_quality = test_case["expected_quality"]

        # Check confidence threshold
        if query.confidence_score < min_confidence:
            return False

        # Check basic query structure
        if not query.query_string.startswith("site:linkedin.com/in"):
            return False

        if len(query.exclusion_terms) < 3:  # Should have some exclusions
            return False

        return True

    def generate_test_report(self, all_results: List[TestResult], benchmark_results: List[BenchmarkResult]) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append("=" * 80)
        report.append("SERP SCANNER AI QUALITY TEST REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary Statistics
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r.success)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        avg_confidence = statistics.mean([r.confidence_score for r in all_results if r.confidence_score > 0])
        avg_execution_time = statistics.mean([r.execution_time for r in all_results if r.execution_time > 0])

        report.append("SUMMARY STATISTICS:")
        report.append(f"  Total Tests: {total_tests}")
        report.append(f"  Successful: {successful_tests} ({success_rate:.1f}%)")
        report.append(f"  Average Confidence: {avg_confidence:.3f}")
        report.append(f"  Average Execution Time: {avg_execution_time:.3f}s")
        report.append("")

        # Quality Assessment Breakdown
        quality_counts = {}
        for result in all_results:
            quality = result.quality_assessment.value
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        report.append("QUALITY ASSESSMENT BREAKDOWN:")
        for quality, count in sorted(quality_counts.items(), reverse=True):
            percentage = (count / total_tests * 100) if total_tests > 0 else 0
            report.append(f"  {quality.title()}: {count} ({percentage:.1f}%)")
        report.append("")

        # Test Categories
        category_results = {}
        for result in all_results:
            parts = result.test_name.split('_')
            if len(parts) >= 2:
                category = parts[0] + '_' + parts[1]
                if category not in category_results:
                    category_results[category] = []
                category_results[category].append(result)

        report.append("TEST CATEGORIES:")
        for category, results in category_results.items():
            successful = sum(1 for r in results if r.success)
            total = len(results)
            rate = (successful / total * 100) if total > 0 else 0
            avg_time = statistics.mean([r.execution_time for r in results if r.execution_time > 0])
            report.append(f"  {category.replace('_', ' ').title()}: {successful}/{total} ({rate:.1f}%) - Avg: {avg_time:.3f}s")
        report.append("")

        # Failed Tests
        failed_tests = [r for r in all_results if not r.success]
        if failed_tests:
            report.append("FAILED TESTS:")
            for result in failed_tests:
                report.append(f"  - {result.test_name}: {result.error_message or 'Unknown error'}")
                report.append(f"    Input: {result.input_text}")
            report.append("")

        # Performance Analysis
        performance_results = [r for r in all_results if 'performance' in r.test_name]
        if performance_results:
            report.append("PERFORMANCE ANALYSIS:")
            for result in performance_results:
                status = "✓" if result.success else "✗"
                report.append(f"  {status} {result.test_name}: {result.actual_output}")
            report.append("")

        # Benchmark Results
        if benchmark_results:
            report.append("BENCHMARK COMPARISON:")
            for benchmark in benchmark_results:
                ai_avg_confidence = statistics.mean([r.confidence_score for r in benchmark.ai_only_results])
                ai_avg_time = statistics.mean([r.execution_time for r in benchmark.ai_only_results])
                report.append(f"  {benchmark.test_category}:")
                report.append(f"    AI System - Confidence: {ai_avg_confidence:.3f}, Time: {ai_avg_time:.3f}s")
            report.append("")

        # Recommendations
        report.append("RECOMMENDATIONS:")
        if success_rate >= 90:
            report.append("  ✓ Excellent performance - system ready for production")
        elif success_rate >= 75:
            report.append("  ⚠ Good performance with room for improvement")
        else:
            report.append("  ✗ Significant issues need to be addressed")

        if avg_confidence >= 0.8:
            report.append("  ✓ High confidence scores indicate reliable AI performance")
        elif avg_confidence >= 0.6:
            report.append("  ⚠ Moderate confidence scores - consider tuning thresholds")
        else:
            report.append("  ✗ Low confidence scores - review AI model performance")

        if avg_execution_time <= 2.0:
            report.append("  ✓ Excellent performance with fast response times")
        elif avg_execution_time <= 5.0:
            report.append("  ⚠ Acceptable performance - consider optimization")
        else:
            report.append("  ✗ Slow performance - investigate bottlenecks")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    async def run_all_tests(self) -> Tuple[List[TestResult], List[BenchmarkResult], str]:
        """Run complete test suite and return results."""
        logger.info("Starting comprehensive AI quality testing...")

        ai_generator = AIQueryGenerator()
        all_results = []

        # Run different test categories
        component_results = await self.run_component_extraction_tests(ai_generator)
        query_results = await self.run_query_construction_tests(ai_generator)
        performance_results = await self.run_performance_tests(ai_generator)
        integration_results = await self.run_integration_tests(ai_generator)
        benchmark_results = await self.run_benchmark_comparison(ai_generator)

        all_results.extend(component_results)
        all_results.extend(query_results)
        all_results.extend(performance_results)
        all_results.extend(integration_results)

        # Generate comprehensive report
        report = self.generate_test_report(all_results, benchmark_results)

        return all_results, benchmark_results, report


async def main():
    """Main test execution function."""
    print("🚀 Starting SERP Scanner AI Quality Testing...")
    print("=" * 60)

    tester = AIQualityTester()

    try:
        results, benchmarks, report = await tester.run_all_tests()

        # Print report to console
        print(report)

        # Save report to file
        report_filename = f"ai_quality_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 Detailed report saved to: {report_filename}")

        # Save results as JSON
        results_filename = f"ai_quality_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "results": [asdict(r) for r in results],
            "benchmarks": [asdict(b) for b in benchmarks]
        }

        with open(results_filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, default=str)

        print(f"📊 Raw results saved to: {results_filename}")

        # Return appropriate exit code
        success_rate = sum(1 for r in results if r.success) / len(results) if results else 0
        if success_rate >= 0.9:
            print("✅ All tests passed successfully!")
            return 0
        elif success_rate >= 0.75:
            print("⚠️  Most tests passed, some issues detected.")
            return 0
        else:
            print("❌ Significant test failures detected.")
            return 1

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"❌ Test execution failed: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)