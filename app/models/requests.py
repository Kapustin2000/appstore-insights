"""
Request models for API endpoints.
"""

from pydantic import BaseModel, Field


class CollectRequest(BaseModel):
    """Request model for collect-and-preprocess endpoint."""

    app_id: str = Field(..., description="Apple App Store app ID")
    country: str = Field(default="us", pattern=r"^[a-z]{2}$", description="Country code (2-letter)")
    review_limit: int = Field(default=300, ge=1, le=2000, description="Maximum number of reviews to collect")
    keep_emojis: bool = Field(default=False, description="Whether to keep emojis in cleaned text")
    lowercase: bool = Field(default=True, description="Whether to convert text to lowercase")
    min_tokens: int = Field(default=3, ge=0, description="Minimum number of tokens for a review to be included")
    save_raw: bool = Field(default=False, description="Whether to save raw data to file")
