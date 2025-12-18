"""
LinkedIn scraping service using serp-api-aggregator
"""
import time
import sys
import os
import re
from typing import Dict, Optional

# Add serp-api-aggregator to Python path
serp_path = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/skills/serp-api-aggregator/src")
if serp_path not in sys.path:
    sys.path.insert(0, serp_path)

from serp.client import SerpAggregator
from models import LinkedInProfile


def parse_company_description(description: str) -> Dict[str, Optional[any]]:
    """
    Parse company description to extract structured data

    Example description:
    "Vertilogic. Jasa TI dan Konsultan TI. Ukuran perusahaan: 2-10 karyawan.
    Kantor Pusat: Jakarta, DKI Jakarta. Jenis: Perseroan Tertutup.
    Tahun Pendirian: 2015. Spesialisasi: ..."

    Returns:
        Dict with parsed fields: industry, location, followers, company_size, etc.
    """
    if not description:
        return {}

    parsed = {}

    # Extract industry (first sentence after company name, before location)
    # Pattern: "Company Name. Industry Type. Location..."
    industry_match = re.search(r'\.([^.]+?)\.\s*(?:Ukuran|Kantor|Jenis|Tahun|\d+\s+pengikut|[A-Z][a-z]+,)', description)
    if not industry_match:
        # Alternative: industry might be before location pattern "City, Country"
        industry_match = re.search(r'\.([^.]+?)\.\s*[A-Z][a-z]+,\s*[A-Z]', description)
    if industry_match:
        parsed['industry'] = industry_match.group(1).strip()

    # Extract followers: "X pengikut" or "X followers"
    followers_match = re.search(r'([\d.,]+)\s+(?:pengikut|followers)', description, re.IGNORECASE)
    if followers_match:
        followers_str = followers_match.group(1).replace('.', '').replace(',', '')
        try:
            parsed['followers'] = int(followers_str)
        except ValueError:
            pass

    # Extract company size: "Ukuran perusahaan: X karyawan"
    size_match = re.search(r'Ukuran perusahaan:\s*([^.]+?)(?:\.|$)', description, re.IGNORECASE)
    if size_match:
        parsed['company_size'] = size_match.group(1).strip()

    # Extract headquarters: "Kantor Pusat: Location"
    hq_match = re.search(r'Kantor Pusat:\s*([^.]+?)(?:\.|$)', description, re.IGNORECASE)
    if hq_match:
        parsed['headquarters'] = hq_match.group(1).strip()

    # Extract company type: "Jenis: Type"
    type_match = re.search(r'Jenis:\s*([^.]+?)(?:\.|$)', description, re.IGNORECASE)
    if type_match:
        parsed['company_type'] = type_match.group(1).strip()

    # Extract founded year: "Tahun Pendirian: YYYY"
    year_match = re.search(r'Tahun Pendirian:\s*(\d{4})', description, re.IGNORECASE)
    if year_match:
        try:
            parsed['founded_year'] = int(year_match.group(1))
        except ValueError:
            pass

    # Extract location from "City, Country" pattern if not HQ
    if 'headquarters' not in parsed:
        location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', description)
        if location_match:
            parsed['location'] = f"{location_match.group(1)}, {location_match.group(2)}"
    else:
        parsed['location'] = parsed['headquarters']

    return parsed


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

    Fetch pages sampai mendapat target jumlah profiles (max_pages * 10)
    atau mencapai batas maksimum pages.

    Args:
        role: Job role atau position (e.g., 'IT Programmer')
        location: Location/city (e.g., 'Jakarta', 'Singapore')
        country: Country code (default: 'us')
        language: Language code (default: 'en')
        max_pages: Target pages - akan fetch sampai dapat (max_pages * 10) profiles
        site_filter: LinkedIn content type (profile, posts, jobs, company, all)

    Returns:
        Dict dengan hasil scraping
    """
    start_time = time.time()

    # Build query - auto-detect site filter from role
    # If role already contains linkedin.com/company, jangan tambahkan linkedin.com/in/
    # Otherwise, tambahkan linkedin.com/in/ untuk profile search
    if "linkedin.com/company" in role:
        # Company search - role sudah lengkap dengan linkedin.com/company
        query = role
        url_filter = "linkedin.com/company"
    else:
        # Profile search - tambahkan linkedin.com/in/
        query = f"{role} linkedin.com/in/"
        url_filter = "linkedin.com/in/"

    if location.strip():
        query += f" {location.strip()}"

    # Calculate target profiles: EXACTLY max_pages * 10
    target_profiles = max_pages * 10

    # Fetch strategy: Fetch extra pages to ensure we get enough after filtering
    # Profile search: ~60-70% results are profiles (rest filtered out)
    # Company search: ~50-60% results are companies (rest filtered out)
    # Fetch 5x pages to ensure we have enough after filtering
    fetch_pages = max_pages * 5

    # Initialize SERP client with async context manager
    async with SerpAggregator() as client:
        # Fetch pages from Google
        result = await client.search(
            query=query,
            country=country,
            language=language,
            max_pages=fetch_pages,
            use_cache=False
        )

        pages_scraped = result.pages_fetched

        # Parse hasil SERP dan filter by site type
        profiles = []
        for organic_result in result.organic:
            if url_filter in organic_result.link:
                # Parse title untuk extract name dan headline
                # Format biasa: "Name - Headline at Company"
                title_parts = organic_result.title.split(' - ', 1)
                name = title_parts[0].strip()
                headline = title_parts[1].strip() if len(title_parts) > 1 else None

                # Get SERP description/snippet
                description = organic_result.description or ""

                # Parse company data if this is a company search
                parsed_data = {}
                if url_filter == "linkedin.com/company":
                    parsed_data = parse_company_description(description)

                profile = LinkedInProfile(
                    name=name,
                    headline=headline,
                    description=description,
                    location=parsed_data.get('location'),
                    company=None,
                    education=None,
                    connections=None,
                    profile_url=organic_result.link,
                    rank=organic_result.rank,
                    best_position=organic_result.best_position,
                    frequency=organic_result.frequency,
                    pages_seen=organic_result.pages_seen,
                    # Company-specific parsed fields
                    industry=parsed_data.get('industry'),
                    followers=parsed_data.get('followers'),
                    company_size=parsed_data.get('company_size'),
                    founded_year=parsed_data.get('founded_year'),
                    company_type=parsed_data.get('company_type'),
                    headquarters=parsed_data.get('headquarters')
                )
                profiles.append(profile)

                # Stop once we have enough profiles (optimization)
                if len(profiles) >= target_profiles:
                    break

        # Truncate to EXACTLY target_profiles
        if len(profiles) > target_profiles:
            profiles = profiles[:target_profiles]

    # Sort profiles by best_position (ascending), then by frequency (descending)
    profiles.sort(key=lambda p: (p.best_position, -p.frequency))

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
            "pages_scraped": pages_scraped,
            "target_profiles": target_profiles,
            "time_taken_seconds": round(time_taken, 2)
        }
    }


def validate_linkedin_url(url: str) -> bool:
    """Validate if URL is a LinkedIn profile"""
    return "linkedin.com/in/" in url.lower()
