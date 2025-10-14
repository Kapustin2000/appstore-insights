"""
Validation utilities.
"""

import re

from ..core.exceptions import ValidationError


def clean_app_id(app_id: str) -> str:
    """
    Clean and validate app ID.

    Removes 'id' prefix if present and validates that the ID contains only digits.

    Args:
        app_id: Raw app ID (e.g., "id1459969523" or "1459969523")

    Returns:
        Cleaned app ID (e.g., "1459969523")

    Raises:
        ValidationError: If app ID is invalid
    """
    if not app_id:
        raise ValidationError("App ID cannot be empty")

    # Remove 'id' prefix if present (case insensitive)
    cleaned_id = re.sub(r"^id", "", app_id, flags=re.IGNORECASE)

    # Remove any whitespace
    cleaned_id = cleaned_id.strip()

    # Validate that it contains only digits
    if not cleaned_id.isdigit():
        raise ValidationError(
            f"Invalid app ID format: '{app_id}'. App ID must contain only digits (e.g., '1459969523')"
        )

    # Validate length (Apple App Store IDs are typically 8-10 digits)
    if len(cleaned_id) < 8 or len(cleaned_id) > 10:
        raise ValidationError(f"Invalid app ID length: '{cleaned_id}'. App ID should be 8-10 digits long")

    return cleaned_id


def validate_country_code(country: str) -> str:
    """
    Validate country code.

    Args:
        country: Country code to validate

    Returns:
        Validated country code

    Raises:
        ValidationError: If country code is invalid
    """
    if not country:
        raise ValidationError("Country code cannot be empty")

    if len(country) != 2:
        raise ValidationError("Country code must be a 2-letter code (e.g., 'us', 'gb', 'de')")

    if not country.isalpha():
        raise ValidationError("Country code must contain only letters")

    return country.lower()
