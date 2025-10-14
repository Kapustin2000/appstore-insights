"""
API routes for the application.
"""

import time

from fastapi import APIRouter, HTTPException, Query

from ..core.exceptions import raise_app_not_found, raise_validation_error
from ..models.requests import CollectRequest
from ..models.responses import AppInfoResponse, AppReviewsResponse
from ..models.schemas import CollectResponse
from ..services.app_service import fetch_app_info
from ..services.review_service import review_service
from ..utils.helpers import (
    create_analysis_stub,
    format_processing_time,
    limit_response_data,
)
from ..utils.validators import clean_app_id

# Create router
router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Apple Store Parser API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "app_info": "/app/{app_id}/info",
            "app_reviews": "/app/{app_id}/reviews",
            "collect_and_preprocess": "/app/collect-and-preprocess",
        },
    }


@router.get("/app/{app_id}/info", response_model=AppInfoResponse)
async def get_app_info(app_id: str, country: str = Query(default="us", description="Country code")):
    """
    Get app information from Apple App Store.

    Args:
        app_id: The app ID in the App Store
        country: Country code (default: us)

    Returns:
        App information including details, ratings, etc.
    """
    try:
        # Clean and validate app ID
        cleaned_id = clean_app_id(app_id)

        # Validate country code
        if not country or len(country) != 2:
            raise_validation_error("Country code must be a 2-letter code (e.g., 'us', 'gb', 'de')")

        # Fetch app information
        info = fetch_app_info(cleaned_id, country)
        if info.get("status") != "success" or not info.get("details"):
            raise_app_not_found(cleaned_id, country)

        return AppInfoResponse(status="success", details=info["details"])

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/app/{app_id}/reviews", response_model=AppReviewsResponse)
async def get_app_reviews(app_id: str, country: str = Query(default="us", description="Country code")):
    """
    Get app reviews from Apple App Store.

    Args:
        app_id: The app ID in the App Store
        country: Country code (default: us)

    Returns:
        List of app reviews with ratings, content, and metadata (fixed to 100 reviews).
    """
    try:
        # Clean and validate app ID
        cleaned_id = clean_app_id(app_id)

        # Validate country code
        if not country or len(country) != 2:
            raise_validation_error("Country code must be a 2-letter code (e.g., 'us', 'gb', 'de')")

        # Use review service to get reviews
        result = review_service.collect_and_preprocess_reviews(
            app_id=cleaned_id,
            country=country,
            review_limit=100,
            keep_emojis=False,
            lowercase=True,
            min_tokens=0,  # No filtering for this endpoint
            save_raw=False,
        )

        return AppReviewsResponse(status="success", count=len(result["raw_reviews"]), items=result["raw_reviews"])

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/app/collect-and-preprocess", response_model=CollectResponse)
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
        info = fetch_app_info(cleaned_id, req.country)
        if info.get("status") != "success" or not info.get("details"):
            raise_app_not_found(cleaned_id, req.country)

        app_info = info["details"]

        # Collect and preprocess reviews
        result = review_service.collect_and_preprocess_reviews(
            app_id=cleaned_id,
            country=req.country,
            review_limit=req.review_limit,
            keep_emojis=req.keep_emojis,
            lowercase=req.lowercase,
            min_tokens=req.min_tokens,
            save_raw=req.save_raw,
        )

        # Prepare response
        response = {
            "status": "ok",
            "meta": {
                "app_id": cleaned_id,
                "country": req.country,
                "collected_reviews": result["meta"]["total_collected"],
                "pages_fetched": result["meta"]["pages_fetched"],
                "processing_time_ms": format_processing_time(t0),
            },
            "app_info": app_info,
            "summary": result["summary"],
            "data": {
                "raw_reviews": limit_response_data(result["raw_reviews"]),
                "clean_reviews": limit_response_data(result["clean_reviews"]),
            },
            "analysis_stub": create_analysis_stub(),
        }

        return response

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
