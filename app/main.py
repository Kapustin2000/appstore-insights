import time
from typing import Dict, List, Optional
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Apple Store Parser API",
    description="API for fetching Apple App Store app information and reviews",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


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


def fetch_app_info(app_id: str, country: str) -> AppInfoResponse:
    """Retrieves the current app details for a specified app in Apple App Store.

    Args:
        app_id (str): The id of the app in app store for which to retrieve the details.
        country (str): The country of the Apple App Store for which to retrieve the details.

    Returns:
        AppInfoResponse: Typed response with status and app details.
    """
    try:
        data = requests.get(f"https://itunes.apple.com/{country}/lookup?id={app_id}")
        data.raise_for_status()
        
        app_data = data.json()
        
        return AppInfoResponse(
            status="success",
            details=AppInfoDetails(**app_data),
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch app info: {str(e)}")


def fetch_app_reviews(app_id: str, country: str) -> AppReviewsResponse:
    """Retrieves the current app reviews for a specified app in Apple App Store.

    Args:
        app_id (str): The id of the app in app store for which to retrieve the reviews.
        country (str): The country of the Apple App Store for which to retrieve the details.

    Returns:
        AppReviewsResponse: Typed response with status, count and review items. Fixed to 100 reviews with 1.0s delay.
    """
    try:
        headers = {"User-Agent": "market-agent/1.0"}
        seen, items, page = set(), [], 1

        limit = 100  # Fixed limit
        while len(items) < limit:
            url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/page={page}/json"
            r = requests.get(url, headers=headers, timeout=15)
            
            if r.status_code != 200:
                break
                
            js = r.json()
            entries = (js.get("feed", {}) or {}).get("entry", []) or []
            added = 0

            for e in entries:
                if "im:rating" not in e:  # skip metadata row
                    continue
                rid = ((e.get("id", {}) or {}).get("label"))
                if rid and rid not in seen:
                    seen.add(rid)
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

            links = (js.get("feed", {}) or {}).get("link", []) or []
            has_next = any((l.get("attributes", {}) or {}).get("rel") == "next" for l in links)
            if not has_next or added == 0:
                break

            page += 1
            time.sleep(1.0)  # Fixed delay of 1 second

        return AppReviewsResponse(
            status="success", 
            count=len(items), 
            items=[ReviewItem(**item) for item in items]
        )
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch app reviews: {str(e)}")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
