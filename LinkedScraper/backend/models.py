"""
Pydantic models for request/response validation
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for LinkedIn search"""
    role: str = Field(..., description="Job role atau position (e.g., 'software engineer', 'data scientist')")
    location: str = Field(default="", description="Location/city (e.g., 'Jakarta', 'Singapore', 'New York')")
    country: str = Field(default="us", description="Country code (e.g., 'us', 'uk', 'id')")
    language: str = Field(default="en", description="Language code (e.g., 'en', 'id')")
    max_pages: int = Field(default=5, ge=1, le=25, description="Maximum pages to scrape (1-25)")
    site_filter: str = Field(default="profile", description="LinkedIn content type filter (profile, posts, jobs, company, all)")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "IT Programmer",
                "location": "Jakarta",
                "country": "id",
                "language": "id",
                "max_pages": 2
            }
        }


class LinkedInProfile(BaseModel):
    """Single LinkedIn profile result with parsed data"""
    name: str
    headline: Optional[str] = None
    description: Optional[str] = None  # SERP snippet/description (raw text)
    location: Optional[str] = None
    company: Optional[str] = None
    education: Optional[str] = None
    connections: Optional[int] = None
    profile_url: str
    rank: int
    best_position: int
    frequency: int
    pages_seen: List[int]

    # Company-specific fields (parsed from description)
    industry: Optional[str] = None
    followers: Optional[int] = None
    company_size: Optional[str] = None
    founded_year: Optional[int] = None
    company_type: Optional[str] = None
    headquarters: Optional[str] = None


class SearchResponse(BaseModel):
    """Response model for LinkedIn search"""
    success: bool
    query: str
    total_results: int
    profiles: List[LinkedInProfile]
    metadata: dict

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "query": "IT Programmer linkedin.com/in/ Jakarta",
                "total_results": 20,
                "profiles": [
                    {
                        "name": "Galih Irawan",
                        "headline": "IT Support as Freelance",
                        "location": "Jawa Barat",
                        "company": "Companies",
                        "education": "Universitas Gunadarma",
                        "connections": 70,
                        "profile_url": "https://id.linkedin.com/in/galihirawan",
                        "rank": 1,
                        "best_position": 1,
                        "frequency": 1,
                        "pages_seen": [1]
                    }
                ],
                "metadata": {
                    "country": "id",
                    "language": "id",
                    "pages_requested": 2,
                    "pages_scraped": 2,
                    "time_taken_seconds": 3.38
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None
