"""
Sentiment analysis service using VADER.
"""
import re
from typing import Dict, List, Tuple, Any
from collections import Counter

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.data import find
    import nltk
except ImportError:
    SentimentIntensityAnalyzer = None
    nltk = None

from ..core.exceptions import ValidationError


class SentimentService:
    """Service for sentiment analysis using VADER."""
    
    def __init__(self):
        self._vader = None
        self._initialize_vader()
    
    def _initialize_vader(self):
        """Initialize VADER sentiment analyzer."""
        if SentimentIntensityAnalyzer is None:
            raise ImportError("NLTK not installed. Please install with: pip install nltk")
        
        try:
            # Try to find existing vader_lexicon
            find('vader_lexicon')
            self._vader = SentimentIntensityAnalyzer()
        except LookupError:
            # Download vader_lexicon if not found
            try:
                nltk.download('vader_lexicon', quiet=True)
                self._vader = SentimentIntensityAnalyzer()
            except Exception as e:
                raise ImportError(f"Failed to download VADER lexicon: {e}")
    
    def analyze_sentiment(
        self, 
        reviews: List[Dict[str, Any]], 
        weights: Dict[str, float] = None,
        thresholds: Dict[str, float] = None
    ) -> Tuple[List[float], List[str], Dict[str, float]]:
        """
        Analyze sentiment for a list of reviews.
        
        Args:
            reviews: List of review dictionaries
            weights: Weights for text vs stars (default: {"text": 0.6, "stars": 0.4})
            thresholds: Classification thresholds (default: {"neg": -0.2, "pos": 0.2})
            
        Returns:
            Tuple of (scores, classifications, overview)
        """
        if weights is None:
            weights = {"text": 0.6, "stars": 0.4}
        if thresholds is None:
            thresholds = {"neg": -0.2, "pos": 0.2}
        
        scores = []
        classifications = []
        
        for review in reviews:
            # Combine title and content
            text = f"{(review.get('title', '') or '').strip()} {(review.get('content', '') or '').strip()}".strip()
            
            # Get VADER compound score
            if self._vader and text:
                vader_score = self._vader.polarity_scores(text)['compound']
            else:
                vader_score = 0.0
            
            # Get star-based score
            rating = int(review.get('rating', 0))
            star_score = (rating - 3) / 2  # Normalize to [-1, 1]
            
            # Combine scores
            combined_score = weights["text"] * vader_score + weights["stars"] * star_score
            scores.append(combined_score)
            
            # Classify
            if combined_score < thresholds["neg"]:
                classifications.append("neg")
            elif combined_score > thresholds["pos"]:
                classifications.append("pos")
            else:
                classifications.append("neu")
        
        # Calculate overview
        total = len(classifications)
        if total == 0:
            overview = {"pos": 0.0, "neu": 0.0, "neg": 0.0, "mean_star": 0.0}
        else:
            counter = Counter(classifications)
            overview = {
                "pos": round(counter["pos"] / total, 3),
                "neu": round(counter["neu"] / total, 3),
                "neg": round(counter["neg"] / total, 3),
                "mean_star": round(sum(int(r.get('rating', 0)) for r in reviews) / total, 2)
            }
        
        return scores, classifications, overview
    
    def get_negative_reviews(
        self, 
        reviews: List[Dict[str, Any]], 
        scores: List[float],
        thresholds: Dict[str, float] = None
    ) -> List[Dict[str, Any]]:
        """
        Get reviews classified as negative.
        
        Args:
            reviews: List of review dictionaries
            scores: Sentiment scores
            thresholds: Classification thresholds
            
        Returns:
            List of negative reviews
        """
        if thresholds is None:
            thresholds = {"neg": -0.2}
        
        negative_reviews = []
        for i, (review, score) in enumerate(zip(reviews, scores)):
            rating = int(review.get('rating', 0))
            if score < thresholds["neg"] or rating <= 2:
                negative_reviews.append({
                    **review,
                    'sentiment_score': score,
                    'index': i
                })
        
        return negative_reviews


# Global service instance
sentiment_service = SentimentService()
