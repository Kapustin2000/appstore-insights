"""
Review processing service.
"""

import json
import os
import time
from typing import Any, Dict, List

from ..core.exceptions import raise_iTunes_api_error, raise_reviews_not_found
from .app_service import fetch_reviews_paged
from .text_service import clean_text, detect_language, summarize_stars, tokenize_en


class ReviewService:
    """Service for processing app reviews."""

    def __init__(self):
        self.data_dir = "data"

    def collect_and_preprocess_reviews(
        self,
        app_id: str,
        country: str,
        review_limit: int = 300,
        keep_emojis: bool = False,
        lowercase: bool = True,
        min_tokens: int = 3,
        save_raw: bool = False,
    ) -> Dict[str, Any]:
        """
        Collect and preprocess app reviews.

        Args:
            app_id: Apple App Store app ID
            country: Country code
            review_limit: Maximum number of reviews to collect
            keep_emojis: Whether to keep emojis in cleaned text
            lowercase: Whether to convert text to lowercase
            min_tokens: Minimum number of tokens for a review to be included
            save_raw: Whether to save raw data to file

        Returns:
            Dictionary with processed review data
        """
        # Fetch reviews with pagination
        reviews = fetch_reviews_paged(app_id=app_id, country=country, limit=review_limit, delay=1.0)

        if reviews.get("status") != "success":
            raise_iTunes_api_error(f"Failed to fetch reviews: {reviews.get('error', 'Unknown error')}")

        items = reviews["items"]

        if not items:
            raise_reviews_not_found(app_id, country)

        # Preprocess reviews
        clean_items = self._preprocess_reviews(items, keep_emojis, lowercase, min_tokens)

        # Calculate summary statistics
        mean_star, by_star = summarize_stars(items)

        # Language distribution
        lang_dist = self._calculate_language_distribution(clean_items)

        # Optional: Save raw data to file
        if save_raw:
            self._save_raw_data(app_id, country, items)

        return {
            "raw_reviews": items,
            "clean_reviews": clean_items,
            "summary": {"mean_star": mean_star, "by_star": by_star, "lang_distribution": lang_dist},
            "meta": {
                "pages_fetched": reviews["meta"]["pages_fetched"],
                "total_collected": len(items),
                "total_cleaned": len(clean_items),
            },
        }

    def _preprocess_reviews(
        self, items: List[Dict], keep_emojis: bool, lowercase: bool, min_tokens: int
    ) -> List[Dict[str, Any]]:
        """Preprocess review items."""
        clean_items = []

        for r in items:
            # Combine title and content
            raw_text = f"{(r.get('title') or '').strip()} {(r.get('content') or '').strip()}".strip()

            # Clean text
            ct = clean_text(raw_text, keep_emojis=keep_emojis, lowercase=lowercase)

            # Tokenize
            toks = tokenize_en(ct)

            # Filter by minimum tokens
            if len(toks) < min_tokens:
                continue

            clean_items.append(
                {"reviewId": r.get("reviewId"), "clean_text": ct, "tokens": toks, "token_count": len(toks)}
            )

        return clean_items

    def _calculate_language_distribution(self, clean_items: List[Dict]) -> Dict[str, float]:
        """Calculate language distribution."""
        en_count = sum(1 for ci in clean_items if detect_language(ci["clean_text"]) == "en")
        total_clean = len(clean_items)

        return {"en": round(en_count / max(1, total_clean), 3), "other": round(1 - (en_count / max(1, total_clean)), 3)}

    def _save_raw_data(self, app_id: str, country: str, items: List[Dict]) -> None:
        """Save raw data to JSONL file."""
        os.makedirs(self.data_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d")
        filename = f"{self.data_dir}/{app_id}_{country}_{timestamp}.jsonl"

        with open(filename, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")


# Global service instance
review_service = ReviewService()
