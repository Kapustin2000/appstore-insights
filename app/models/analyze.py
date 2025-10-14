"""
Models for analysis endpoint.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request model for analyze endpoint."""
    
    app_id: str = Field(..., description="Apple App Store app ID")
    country: str = Field(default="us", pattern=r"^[a-z]{2}$", description="Country code (2-letter)")
    review_limit: int = Field(default=300, ge=1, le=2000, description="Maximum number of reviews to collect")
    use_cached_collect: bool = Field(default=True, description="Whether to use cached collection results")
    sentiment_model: str = Field(default="vader", pattern=r"^(vader|xlm-roberta)$", description="Sentiment analysis model")
    ngram_range: List[int] = Field(default=[1, 2], description="N-gram range for phrase extraction")
    min_df: int = Field(default=2, ge=1, description="Minimum document frequency for phrases")
    top_k_phrases: int = Field(default=20, ge=1, le=100, description="Number of top phrases to return")
    weights: Dict[str, float] = Field(default={"text": 0.6, "stars": 0.4}, description="Weights for sentiment calculation")
    recency_cutoffs_days: List[int] = Field(default=[90, 365], description="Recency cutoff days for weighting")
    reviews_override: Optional[List[Dict[str, Any]]] = Field(default=None, description="Override reviews data")


class SentimentOverview(BaseModel):
    """Sentiment overview statistics."""
    
    pos: float = Field(..., description="Positive sentiment proportion")
    neu: float = Field(..., description="Neutral sentiment proportion")
    neg: float = Field(..., description="Negative sentiment proportion")
    mean_star: float = Field(..., description="Mean star rating")


class NegativePhrase(BaseModel):
    """Negative phrase with statistics."""
    
    phrase: str = Field(..., description="The phrase text")
    score: float = Field(..., description="TF-IDF score")
    count: int = Field(..., description="Number of occurrences")
    share_neg: float = Field(..., description="Share among negative reviews")


class Insight(BaseModel):
    """Actionable insight with prioritization."""
    
    priority: int = Field(..., description="Priority ranking (1=highest)")
    area: str = Field(..., description="Area of concern (e.g., Monetization, UX)")
    issue: str = Field(..., description="Specific issue description")
    why: str = Field(..., description="Explanation of why this is important")
    action: str = Field(..., description="Recommended action")
    impact: str = Field(..., description="Expected impact level")


class DebugInfo(BaseModel):
    """Debug information for analysis."""
    
    model: str = Field(..., description="Sentiment model used")
    thresholds: Dict[str, float] = Field(..., description="Classification thresholds")
    low_sample: bool = Field(default=False, description="Whether sample size is low")
    no_negative_signal: bool = Field(default=False, description="Whether no negative signal found")


class AnalyzeResponse(BaseModel):
    """Response model for analyze endpoint."""
    
    status: str = Field(..., description="Response status")
    meta: Dict[str, Any] = Field(..., description="Metadata about the analysis")
    sentiment_overview: SentimentOverview = Field(..., description="Sentiment statistics")
    top_negative_phrases: List[NegativePhrase] = Field(..., description="Top negative phrases")
    insights: List[Insight] = Field(..., description="Actionable insights")
    debug: DebugInfo = Field(..., description="Debug information")
