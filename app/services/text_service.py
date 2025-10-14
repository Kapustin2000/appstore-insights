"""
Text preprocessing module for cleaning and tokenizing review text.
"""

import html
import re
from collections import Counter
from statistics import mean
from typing import Dict, List, Optional, Tuple

import emoji
import ftfy
from bs4 import BeautifulSoup

# Regex patterns for text cleaning
URL_RE = re.compile(r"https?://\S+|www\.\S+")
EMAIL_RE = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")
MENTION_RE = re.compile(r"[@#]\w+")
WS_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z']{2,}")


def clean_text(text: str, keep_emojis: bool = False, lowercase: bool = True) -> str:
    """
    Clean and normalize text content.

    Args:
        text: Raw text to clean
        keep_emojis: Whether to keep emojis in the text
        lowercase: Whether to convert to lowercase

    Returns:
        Cleaned text string
    """
    if not text:
        return ""

    # Fix encoding issues
    t = ftfy.fix_text(text)

    # Decode HTML entities
    t = html.unescape(t)

    # Remove HTML tags
    t = BeautifulSoup(t, "lxml").get_text(separator=" ")

    # Remove URLs
    t = URL_RE.sub(" ", t)

    # Remove email addresses
    t = EMAIL_RE.sub(" ", t)

    # Remove mentions and hashtags
    t = MENTION_RE.sub(" ", t)

    # Handle emojis
    if not keep_emojis:
        t = emoji.replace_emoji(t, replace=" ")

    # Convert to lowercase if requested
    if lowercase:
        t = t.lower()

    # Normalize whitespace
    t = WS_RE.sub(" ", t).strip()

    return t


def tokenize_en(text: str) -> List[str]:
    """
    Tokenize English text using regex pattern.

    Args:
        text: Text to tokenize

    Returns:
        List of tokens
    """
    return TOKEN_RE.findall(text or "")


def summarize_stars(reviews: List[Dict]) -> Tuple[Optional[float], Dict[str, int]]:
    """
    Calculate star rating summary statistics.

    Args:
        reviews: List of review dictionaries with 'rating' field

    Returns:
        Tuple of (mean_rating, rating_distribution)
    """
    stars = [int(r.get("rating", 0)) for r in reviews if r.get("rating")]
    by_star = {str(k): v for k, v in dict(Counter(stars)).items()}
    mean_rating = round(mean(stars), 2) if stars else None
    return mean_rating, by_star


def detect_language(text: str) -> str:
    """
    Simple language detection based on ASCII character ratio.

    Args:
        text: Text to analyze

    Returns:
        Language code ('en' or 'other')
    """
    if not text:
        return "other"

    ascii_letters = sum(ch.isascii() and ch.isalpha() for ch in text)
    total_letters = sum(ch.isalpha() for ch in text)

    if total_letters == 0:
        return "other"

    ascii_ratio = ascii_letters / total_letters
    return "en" if ascii_ratio >= 0.8 else "other"
