import time
import re
import os
from typing import Dict, List, Optional, Any
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator

# Import our custom modules
from .sources import fetch_app_info as fetch_app_info_new, fetch_reviews_paged
from .textprep import clean_text, tokenize_en, summarize_stars, detect_language

app = FastAPI(
    title="Apple Store Parser API",
    description="API for fetching Apple App Store app information and reviews",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


def clean_app_id(app_id: str) -> str:
    """
    Clean and validate app ID.
    
    Removes 'id' prefix if present and validates that the ID contains only digits.
    
    Args:
        app_id: Raw app ID (e.g., "id1566419183" or "1566419183")
        
    Returns:
        Cleaned app ID (e.g., "1566419183")
        
    Raises:
        ValueError: If app ID is invalid
    """
    if not app_id:
        raise ValueError("App ID cannot be empty")
    
    # Remove 'id' prefix if present (case insensitive)
    cleaned_id = re.sub(r'^id', '', app_id, flags=re.IGNORECASE)
    
    # Remove any whitespace
    cleaned_id = cleaned_id.strip()
    
    # Validate that it contains only digits
    if not cleaned_id.isdigit():
        raise ValueError(f"Invalid app ID format: '{app_id}'. App ID must contain only digits (e.g., '1566419183')")
    
    # Validate length (Apple App Store IDs are typically 8-10 digits)
    if len(cleaned_id) < 8 or len(cleaned_id) > 10:
        raise ValueError(f"Invalid app ID length: '{cleaned_id}'. App ID should be 8-10 digits long")
    
    return cleaned_id


class ReviewItem(BaseModel):
    reviewId: str = Field(..., description="Unique identifier for the review")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, description="Review title")
    content: Optional[str] = Field(None, description="Review content/body")
    updated: Optional[str] = Field(None, description="Date when the review was last updated")
    version: Optional[str] = Field(None, description="App version when review was written")
    author: Optional[str] = Field(None, description="Review author name")


class AppReviewsResponse(BaseModel):
    status: str = Field(..., description="Response status")
    count: int = Field(..., ge=0, description="Number of reviews returned")
    items: List[ReviewItem] = Field(..., description="List of review items")


class AppInfo(BaseModel):
    trackId: int = Field(..., description="Unique app identifier")
    trackName: str = Field(..., description="App name")
    bundleId: str = Field(..., description="App bundle identifier")
    version: str = Field(..., description="Current app version")
    price: float = Field(..., description="App price")
    formattedPrice: str = Field(..., description="Formatted price string")
    description: str = Field(..., description="App description")
    averageUserRating: float = Field(..., description="Average user rating")
    userRatingCount: int = Field(..., description="Total number of user ratings")
    averageUserRatingForCurrentVersion: float = Field(..., description="Average rating for current version")
    userRatingCountForCurrentVersion: int = Field(..., description="Number of ratings for current version")
    releaseDate: str = Field(..., description="App release date")
    currentVersionReleaseDate: str = Field(..., description="Current version release date")
    releaseNotes: Optional[str] = Field(None, description="Release notes for current version")
    artistName: str = Field(..., description="Developer name")
    artistId: int = Field(..., description="Developer ID")
    sellerName: str = Field(..., description="Seller name")
    primaryGenreName: str = Field(..., description="Primary genre")
    genres: List[str] = Field(..., description="List of genres")
    contentAdvisoryRating: str = Field(..., description="Content advisory rating")
    minimumOsVersion: str = Field(..., description="Minimum required iOS version")
    fileSizeBytes: str = Field(..., description="App file size in bytes")
    languageCodesISO2A: List[str] = Field(..., description="Supported languages")
    screenshotUrls: List[str] = Field(..., description="iPhone screenshot URLs")
    ipadScreenshotUrls: List[str] = Field(..., description="iPad screenshot URLs")
    artworkUrl60: str = Field(..., description="60x60 app icon URL")
    artworkUrl100: str = Field(..., description="100x100 app icon URL")
    artworkUrl512: str = Field(..., description="512x512 app icon URL")
    trackViewUrl: str = Field(..., description="App Store URL")
    artistViewUrl: str = Field(..., description="Developer page URL")
    sellerUrl: Optional[str] = Field(None, description="Seller website URL")


class AppInfoDetails(BaseModel):
    resultCount: int = Field(..., description="Number of results returned")
    results: List[AppInfo] = Field(..., description="List of app information")


class AppInfoResponse(BaseModel):
    status: str = Field(..., description="Response status")
    details: AppInfoDetails = Field(..., description="App information details from iTunes API")


# New models for collect-and-preprocess endpoint
class CollectRequest(BaseModel):
    app_id: str = Field(..., description="Apple App Store app ID")
    country: str = Field(default="us", pattern=r"^[a-z]{2}$", description="Country code (2-letter)")
    review_limit: int = Field(default=300, ge=1, le=2000, description="Maximum number of reviews to collect")
    keep_emojis: bool = Field(default=False, description="Whether to keep emojis in cleaned text")
    lowercase: bool = Field(default=True, description="Whether to convert text to lowercase")
    min_tokens: int = Field(default=3, ge=0, description="Minimum number of tokens for a review to be included")
    save_raw: bool = Field(default=False, description="Whether to save raw data to file")


class ReviewRaw(BaseModel):
    reviewId: str = Field(..., description="Unique review identifier")
    rating: int = Field(..., ge=1, le=5, description="Star rating")
    title: Optional[str] = Field(None, description="Review title")
    content: Optional[str] = Field(None, description="Review content")
    updated: Optional[str] = Field(None, description="Last update timestamp")
    version: Optional[str] = Field(None, description="App version")
    author: Optional[str] = Field(None, description="Review author")


class ReviewClean(BaseModel):
    reviewId: str = Field(..., description="Unique review identifier")
    clean_text: str = Field(..., description="Cleaned and normalized text")
    tokens: List[str] = Field(..., description="List of tokens")
    token_count: int = Field(..., description="Number of tokens")


class Summary(BaseModel):
    mean_star: Optional[float] = Field(None, description="Average star rating")
    by_star: Dict[str, int] = Field(..., description="Distribution of ratings by star count")
    lang_distribution: Dict[str, float] = Field(..., description="Language distribution")


class CollectResponse(BaseModel):
    status: str = Field(..., description="Response status")
    meta: Dict[str, Any] = Field(..., description="Metadata about the collection process")
    app_info: Dict[str, Any] = Field(..., description="App information")
    summary: Summary = Field(..., description="Summary statistics")
    data: Dict[str, List] = Field(..., description="Raw and cleaned review data")
    analysis_stub: Dict[str, Optional[str]] = Field(..., description="Placeholder for future analysis")


def fetch_app_info(app_id: str, country: str) -> AppInfoResponse:
    """Retrieves the current app details for a specified app in Apple App Store.

    Args:
        app_id (str): The id of the app in app store for which to retrieve the details.
        country (str): The country of the Apple App Store for which to retrieve the details.

    Returns:
        AppInfoResponse: Typed response with status and app details.
    """
    try:
        # Clean and validate app ID
        cleaned_id = clean_app_id(app_id)
        
        # Validate country code (basic validation)
        if not country or len(country) != 2:
            raise ValueError("Country code must be a 2-letter code (e.g., 'us', 'gb', 'de')")
        
        data = requests.get(f"https://itunes.apple.com/{country}/lookup?id={cleaned_id}", timeout=10)
        data.raise_for_status()
        
        app_data = data.json()
        
        # Check if app was found
        if app_data.get("resultCount", 0) == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"App with ID '{cleaned_id}' not found in {country.upper()} App Store"
            )
        
        return AppInfoResponse(
            status="success",
            details=AppInfoDetails(**app_data),
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch app info from iTunes API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def fetch_app_reviews(app_id: str, country: str) -> AppReviewsResponse:
    """Retrieves the current app reviews for a specified app in Apple App Store.

    Args:
        app_id (str): The id of the app in app store for which to retrieve the reviews.
        country (str): The country of the Apple App Store for which to retrieve the details.

    Returns:
        AppReviewsResponse: Typed response with status, count and review items. Fixed to 100 reviews with 1.0s delay.
    """
    try:
        # Clean and validate app ID
        cleaned_id = clean_app_id(app_id)
        
        # Validate country code (basic validation)
        if not country or len(country) != 2:
            raise ValueError("Country code must be a 2-letter code (e.g., 'us', 'gb', 'de')")
        
        headers = {"User-Agent": "market-agent/1.0"}
        seen, items, page = set(), [], 1
        max_retries = 3

        limit = 100  # Fixed limit
        while len(items) < limit:
            url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={cleaned_id}/sortBy=mostRecent/page={page}/json"
            
            # Retry logic for failed requests
            for attempt in range(max_retries):
                try:
                    r = requests.get(url, headers=headers, timeout=15)
                    r.raise_for_status()
                    break
                except requests.RequestException as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(1.0)  # Wait before retry
            
            js = r.json()
            
            # Check if feed exists and has entries
            feed = js.get("feed", {})
            if not feed:
                break
                
            entries = feed.get("entry", []) or []
            added = 0

            for e in entries:
                if "im:rating" not in e:  # skip metadata row
                    continue
                rid = ((e.get("id", {}) or {}).get("label"))
                if rid and rid not in seen:
                    seen.add(rid)
                    try:
                        items.append({
                            "reviewId": rid,
                            "rating": int(((e.get("im:rating", {}) or {}).get("label") or "0")),
                            "title": ((e.get("title", {}) or {}).get("label")),
                            "content": ((e.get("content", {}) or {}).get("label")),
                            "updated": ((e.get("updated", {}) or {}).get("label")),
                            "version": ((e.get("im:version", {}) or {}).get("label")),
                            "author": (((e.get("author", {}) or {}).get("name", {}) or {}).get("label")),
                        })
                        added += 1
                        if len(items) >= limit:
                            break
                    except (ValueError, TypeError) as e:
                        # Skip malformed review entries
                        continue

            links = feed.get("link", []) or []
            has_next = any((l.get("attributes", {}) or {}).get("rel") == "next" for l in links)
            if not has_next or added == 0:
                break

            page += 1
            time.sleep(1.0)  # Fixed delay of 1 second

        # Check if we found any reviews
        if not items:
            raise HTTPException(
                status_code=404, 
                detail=f"No reviews found for app ID '{cleaned_id}' in {country.upper()} App Store"
            )

        return AppReviewsResponse(
            status="success", 
            count=len(items), 
            items=[ReviewItem(**item) for item in items]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to fetch app reviews from iTunes API: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Apple Store Parser API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "app_info": "/app/{app_id}/info",
            "app_reviews": "/app/{app_id}/reviews"
        }
    }


@app.get("/app/{app_id}/info", response_model=AppInfoResponse)
async def get_app_info(app_id: str, country: str = "us"):
    """
    Get app information from Apple App Store.
    
    Args:
        app_id: The app ID in the App Store
        country: Country code (default: us)
    
    Returns:
        App information including details, ratings, etc.
    """
    return fetch_app_info(app_id, country)


@app.get("/app/{app_id}/reviews", response_model=AppReviewsResponse)
async def get_app_reviews(
    app_id: str, 
    country: str = Query(default="us", description="Country code")
):
    """
    Get app reviews from Apple App Store.
    
    Args:
        app_id: The app ID in the App Store
        country: Country code (default: us)
    
    Returns:
        List of app reviews with ratings, content, and metadata (fixed to 100 reviews).
    """
    return fetch_app_reviews(app_id, country)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/app/collect-and-preprocess", response_model=CollectResponse)
async def collect_and_preprocess(req: CollectRequest):
    """
    Collect and preprocess app data from Apple App Store.
    
    This endpoint fetches app metadata, collects reviews with pagination,
    cleans and normalizes text, and returns both raw and processed data
    along with summary statistics.
    """
    t0 = time.time()
    
    try:
        # Clean and validate app ID
        cleaned_id = clean_app_id(req.app_id)
        
        # Fetch app information
        info = fetch_app_info_new(cleaned_id, req.country)
        if info.get("status") != "success" or not info.get("details"):
            raise HTTPException(
                status_code=404, 
                detail=f"App with ID '{cleaned_id}' not found in {req.country.upper()} App Store"
            )
        
        app_info = info["details"]
        
        # Fetch reviews with pagination
        reviews = fetch_reviews_paged(
            app_id=cleaned_id,
            country=req.country,
            limit=req.review_limit,
            delay=1.0
        )
        
        if reviews.get("status") != "success":
            raise HTTPException(
                status_code=502, 
                detail=f"Failed to fetch reviews: {reviews.get('error', 'Unknown error')}"
            )
        
        items = reviews["items"]
        
        # Preprocess reviews
        clean_items = []
        for r in items:
            # Combine title and content
            raw_text = f"{(r.get('title') or '').strip()} {(r.get('content') or '').strip()}".strip()
            
            # Clean text
            ct = clean_text(
                raw_text, 
                keep_emojis=req.keep_emojis, 
                lowercase=req.lowercase
            )
            
            # Tokenize
            toks = tokenize_en(ct)
            
            # Filter by minimum tokens
            if len(toks) < req.min_tokens:
                continue
                
            clean_items.append({
                "reviewId": r.get("reviewId"),
                "clean_text": ct,
                "tokens": toks,
                "token_count": len(toks)
            })
        
        # Calculate summary statistics
        mean_star, by_star = summarize_stars(items)
        
        # Language distribution
        en_count = sum(1 for ci in clean_items if detect_language(ci["clean_text"]) == "en")
        total_clean = len(clean_items)
        lang_dist = {
            "en": round(en_count / max(1, total_clean), 3),
            "other": round(1 - (en_count / max(1, total_clean)), 3)
        }
        
        # Optional: Save raw data to file
        if req.save_raw:
            os.makedirs("data", exist_ok=True)
            timestamp = time.strftime("%Y%m%d")
            filename = f"data/{cleaned_id}_{req.country}_{timestamp}.jsonl"
            
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                for item in items:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # Prepare response
        response = {
            "status": "ok",
            "meta": {
                "app_id": cleaned_id,
                "country": req.country,
                "collected_reviews": len(items),
                "pages_fetched": reviews["meta"]["pages_fetched"],
                "processing_time_ms": int((time.time() - t0) * 1000)
            },
            "app_info": app_info,
            "summary": {
                "mean_star": mean_star,
                "by_star": by_star,
                "lang_distribution": lang_dist
            },
            "data": {
                "raw_reviews": items[:50],  # Limit to first 50 for response size
                "clean_reviews": clean_items[:50]
            },
            "analysis_stub": {
                "sentiment": None,
                "topics": None,
                "insights": None
            }
        }
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
