"""
Custom exceptions for the application.
"""

from typing import Optional

from fastapi import HTTPException


class AppStoreParserException(Exception):
    """Base exception for App Store Parser."""

    pass


class AppNotFoundError(AppStoreParserException):
    """Raised when app is not found in App Store."""

    def __init__(self, app_id: str, country: str):
        self.app_id = app_id
        self.country = country
        super().__init__(f"App with ID '{app_id}' not found in {country.upper()} App Store")


class ReviewsNotFoundError(AppStoreParserException):
    """Raised when no reviews are found for an app."""

    def __init__(self, app_id: str, country: str):
        self.app_id = app_id
        self.country = country
        super().__init__(f"No reviews found for app ID '{app_id}' in {country.upper()} App Store")


class iTunesAPIError(AppStoreParserException):
    """Raised when iTunes API returns an error."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(f"iTunes API error: {message}")


class ValidationError(AppStoreParserException):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(f"Validation error: {message}")


# HTTP Exception helpers
def raise_app_not_found(app_id: str, country: str) -> None:
    """Raise HTTP 404 for app not found."""
    raise HTTPException(status_code=404, detail=f"App with ID '{app_id}' not found in {country.upper()} App Store")


def raise_reviews_not_found(app_id: str, country: str) -> None:
    """Raise HTTP 404 for reviews not found."""
    raise HTTPException(
        status_code=404, detail=f"No reviews found for app ID '{app_id}' in {country.upper()} App Store"
    )


def raise_iTunes_api_error(message: str, status_code: int = 503) -> None:
    """Raise HTTP error for iTunes API issues."""
    raise HTTPException(status_code=status_code, detail=f"iTunes API error: {message}")


def raise_validation_error(message: str) -> None:
    """Raise HTTP 400 for validation errors."""
    raise HTTPException(status_code=400, detail=message)
