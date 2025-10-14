"""
Response models for API endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReviewItem(BaseModel):
    """Model for individual review item."""

    reviewId: str = Field(..., description="Unique identifier for the review")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    title: Optional[str] = Field(None, description="Review title")
    content: Optional[str] = Field(None, description="Review content/body")
    updated: Optional[str] = Field(None, description="Date when the review was last updated")
    version: Optional[str] = Field(None, description="App version when review was written")
    author: Optional[str] = Field(None, description="Review author name")


class AppReviewsResponse(BaseModel):
    """Response model for app reviews endpoint."""

    status: str = Field(..., description="Response status")
    count: int = Field(..., ge=0, description="Number of reviews returned")
    items: List[ReviewItem] = Field(..., description="List of review items")


class AppInfo(BaseModel):
    """Model for app information."""

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
    """Model for app info details container."""

    resultCount: int = Field(..., description="Number of results returned")
    results: List[Dict[str, Any]] = Field(..., description="List of app information")


class AppInfoResponse(BaseModel):
    """Response model for app info endpoint."""

    status: str = Field(..., description="Response status")
    details: AppInfoDetails = Field(..., description="App information details from iTunes API")
