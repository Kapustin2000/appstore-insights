"""
Data schemas for collect-and-preprocess endpoint.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReviewRaw(BaseModel):
    """Model for raw review data."""

    reviewId: str = Field(..., description="Unique review identifier")
    rating: int = Field(..., ge=1, le=5, description="Star rating")
    title: Optional[str] = Field(None, description="Review title")
    content: Optional[str] = Field(None, description="Review content")
    updated: Optional[str] = Field(None, description="Last update timestamp")
    version: Optional[str] = Field(None, description="App version")
    author: Optional[str] = Field(None, description="Review author")


class ReviewClean(BaseModel):
    """Model for cleaned review data."""

    reviewId: str = Field(..., description="Unique review identifier")
    clean_text: str = Field(..., description="Cleaned and normalized text")
    tokens: List[str] = Field(..., description="List of tokens")
    token_count: int = Field(..., description="Number of tokens")


class Summary(BaseModel):
    """Model for summary statistics."""

    mean_star: Optional[float] = Field(None, description="Average star rating")
    by_star: Dict[str, int] = Field(..., description="Distribution of ratings by star count")
    lang_distribution: Dict[str, float] = Field(..., description="Language distribution")


class CollectResponse(BaseModel):
    """Response model for collect-and-preprocess endpoint."""

    status: str = Field(..., description="Response status")
    meta: Dict[str, Any] = Field(..., description="Metadata about the collection process")
    app_info: Dict[str, Any] = Field(..., description="App information")
    summary: Summary = Field(..., description="Summary statistics")
    data: Dict[str, List] = Field(..., description="Raw and cleaned review data")
    analysis_stub: Dict[str, Optional[str]] = Field(..., description="Placeholder for future analysis")
