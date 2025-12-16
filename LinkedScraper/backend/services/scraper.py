"""
LinkedIn scraping service using serp-api-aggregator
"""
import time
import sys
import os
from typing import Dict

# Add serp-api-aggregator to Python path
serp_path = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/skills/serp-api-aggregator/src")
if serp_path not in sys.path:
    sys.path.insert(0, serp_path)

from serp.client import SerpAggregator
from models import LinkedInProfile


async def search_linkedin_profiles(
    role: str,
    location: str = "",
    country: str = "us",
    language: str = "en",
    max_pages: int = 5,
    site_filter: str = "profile"
) -> Dict:
    """
    Search LinkedIn profiles menggunakan serp-api-aggregator

    Args:
        role: Job role atau position (e.g., 'IT Programmer')
        location: Location/city (e.g., 'Jakarta', 'Singapore')
        country: Country code (default: 'us')
        language: Language code (default: 'en')
        max_pages: Maximum pages to scrape (default: 5)
        site_filter: LinkedIn content type (profile, posts, jobs, company, all)

    Returns:
        Dict dengan hasil scraping
    """
    start_time = time.time()

    # Build query - gunakan linkedin.com/in/ sebagai keyword (bukan site: operator)
    # Format: "IT Programmer linkedin.com/in/ Jakarta"
    query = f"{role} linkedin.com/in/"
    if location.strip():
        query += f" {location.strip()}"

    # Initialize SERP client with async context manager
    async with SerpAggregator() as client:
        # Search menggunakan serp-aggregator
        result = await client.search(
            query=query,
            country=country,
            language=language,
            max_pages=max_pages,
            use_cache=False
        )

        # Parse hasil SERP ke LinkedIn profiles
        # Backend hanya ambil organic results yang berisi linkedin.com/in/
        profiles = []
        for organic_result in result.organic:
            if 'linkedin.com/in/' in organic_result.link:
                # Parse title untuk extract name dan headline
                # Format biasa: "Name - Headline at Company"
                title_parts = organic_result.title.split(' - ', 1)
                name = title_parts[0].strip()
                headline = title_parts[1].strip() if len(title_parts) > 1 else None

                # Parse description untuk extract location, company, education
                description = organic_result.description or ""

                profile = LinkedInProfile(
                    name=name,
                    headline=headline,
                    location=None,  # Parse dari description jika diperlukan
                    company=None,   # Parse dari description jika diperlukan
                    education=None, # Parse dari description jika diperlukan
                    connections=None,
                    profile_url=organic_result.link,
                    rank=organic_result.rank,
                    best_position=organic_result.best_position,
                    frequency=organic_result.frequency,
                    pages_seen=organic_result.pages_seen
                )
                profiles.append(profile)

    time_taken = time.time() - start_time

    return {
        "success": True,
        "query": query,
        "total_results": len(profiles),
        "profiles": [p.model_dump() for p in profiles],
        "metadata": {
            "country": country,
            "language": language,
            "pages_requested": max_pages,
            "pages_scraped": getattr(result, 'pages_fetched', max_pages),
            "time_taken_seconds": round(time_taken, 2)
        }
    }


def validate_linkedin_url(url: str) -> bool:
    """Validate if URL is a LinkedIn profile"""
    return "linkedin.com/in/" in url.lower()
