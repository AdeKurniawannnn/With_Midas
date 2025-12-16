"""
API routes for LinkedScraper
"""
from fastapi import APIRouter, HTTPException
from models import SearchRequest, SearchResponse, ErrorResponse
from services.scraper import search_linkedin_profiles

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_linkedin(request: SearchRequest):
    """
    Search LinkedIn profiles by role and country

    Example request:
    ```json
    {
        "role": "software engineer",
        "country": "us",
        "language": "en",
        "max_pages": 5
    }
    ```
    """
    try:
        result = await search_linkedin_profiles(
            role=request.role,
            location=request.location,
            country=request.country,
            language=request.language,
            max_pages=request.max_pages,
            site_filter=request.site_filter
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Scraping failed",
                "detail": str(e)
            }
        )


@router.get("/test")
def test_endpoint():
    """Test endpoint untuk verify API works"""
    return {
        "message": "LinkedScraper API is working!",
        "endpoints": {
            "search": "POST /api/search",
            "test": "GET /api/test"
        }
    }
