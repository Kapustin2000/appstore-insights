"""
Insights generation service for actionable recommendations.
"""
import re
from typing import Dict, List, Tuple, Any
from collections import Counter
from datetime import datetime, timedelta

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
except ImportError:
    TfidfVectorizer = None
    ENGLISH_STOP_WORDS = set()

from dateutil import parser as date_parser

from .text_service import clean_text


class InsightsService:
    """Service for generating actionable insights from negative reviews."""
    
    def __init__(self):
        self.phrase_mappings = {
            # Monetization patterns
            'ad': {'area': 'Monetization', 'action': 'Reduce interstitial frequency, add ad-free plan'},
            'ads': {'area': 'Monetization', 'action': 'Reduce interstitial frequency, add ad-free plan'},
            'advert': {'area': 'Monetization', 'action': 'Reduce interstitial frequency, add ad-free plan'},
            'advertisement': {'area': 'Monetization', 'action': 'Reduce interstitial frequency, add ad-free plan'},
            
            # Pricing/IAP patterns
            'pay': {'area': 'Pricing/IAP', 'action': 'Open basic features, add free trial, transparent pricing'},
            'paywall': {'area': 'Pricing/IAP', 'action': 'Open basic features, add free trial, transparent pricing'},
            'unlock': {'area': 'Pricing/IAP', 'action': 'Open basic features, add free trial, transparent pricing'},
            'purchase': {'area': 'Pricing/IAP', 'action': 'Open basic features, add free trial, transparent pricing'},
            'locked': {'area': 'Pricing/IAP', 'action': 'Open basic features, add free trial, transparent pricing'},
            'subscribe': {'area': 'Pricing/IAP', 'action': 'Open basic features, add free trial, transparent pricing'},
            'subscription': {'area': 'Pricing/IAP', 'action': 'Open basic features, add free trial, transparent pricing'},
            
            # Quality patterns
            'bug': {'area': 'Quality', 'action': 'Bug fixes, crash reporting, canary releases'},
            'crash': {'area': 'Quality', 'action': 'Bug fixes, crash reporting, canary releases'},
            'freeze': {'area': 'Quality', 'action': 'Bug fixes, crash reporting, canary releases'},
            'lag': {'area': 'Quality', 'action': 'Bug fixes, crash reporting, canary releases'},
            'slow': {'area': 'Quality', 'action': 'Performance optimization, caching improvements'},
            'glitch': {'area': 'Quality', 'action': 'Bug fixes, crash reporting, canary releases'},
            
            # Core UX patterns
            'write': {'area': 'Core UX', 'action': 'Add/improve key features, conduct UX testing'},
            'space': {'area': 'Core UX', 'action': 'Add/improve key features, conduct UX testing'},
            'feature': {'area': 'Core UX', 'action': 'Add/improve key features, conduct UX testing'},
            'missing': {'area': 'Core UX', 'action': 'Add/improve key features, conduct UX testing'},
            'diary': {'area': 'Core UX', 'action': 'Add/improve key features, conduct UX testing'},
            'interface': {'area': 'Core UX', 'action': 'Improve UX, conduct usability testing'},
            'design': {'area': 'Core UX', 'action': 'Improve UX, conduct usability testing'},
        }
    
    def extract_negative_phrases(
        self, 
        negative_reviews: List[Dict[str, Any]], 
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 2,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Extract top negative phrases using TF-IDF.
        
        Args:
            negative_reviews: List of negative reviews
            ngram_range: N-gram range for phrase extraction
            min_df: Minimum document frequency
            top_k: Number of top phrases to return
            
        Returns:
            List of top negative phrases with statistics
        """
        if not negative_reviews:
            return []
        
        if TfidfVectorizer is None:
            raise ImportError("scikit-learn not installed. Please install with: pip install scikit-learn")
        
        # Prepare texts
        texts = []
        for review in negative_reviews:
            text = f"{(review.get('title', '') or '').strip()} {(review.get('content', '') or '').strip()}".strip()
            cleaned_text = clean_text(text, keep_emojis=False, lowercase=True)
            texts.append(cleaned_text)
        
        if not texts:
            return []
        
        # Adjust min_df for small samples
        actual_min_df = min(min_df, max(1, len(texts) // 10))
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            min_df=actual_min_df,
            stop_words='english',
            max_features=1000
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top phrases
            scores = tfidf_matrix.sum(axis=0).A1
            phrase_scores = list(zip(feature_names, scores))
            phrase_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Filter and format results
            top_phrases = []
            total_neg = len(negative_reviews)
            
            for phrase, score in phrase_scores[:top_k]:
                # Skip pure numbers and single characters
                if re.match(r'^\d+$', phrase) or len(phrase) <= 1:
                    continue
                
                # Count occurrences
                count = sum(1 for text in texts if phrase in text)
                
                top_phrases.append({
                    'phrase': phrase,
                    'score': round(float(score), 3),
                    'count': count,
                    'share_neg': round(count / total_neg, 3)
                })
            
            return top_phrases
            
        except Exception as e:
            # Fallback for small samples
            return self._fallback_phrase_extraction(texts, top_k)
    
    def _fallback_phrase_extraction(self, texts: List[str], top_k: int) -> List[Dict[str, Any]]:
        """Fallback phrase extraction for small samples."""
        # Simple word frequency approach
        word_counts = Counter()
        for text in texts:
            words = text.split()
            for word in words:
                if len(word) > 2 and word not in ENGLISH_STOP_WORDS:
                    word_counts[word] += 1
        
        total_words = sum(word_counts.values())
        top_phrases = []
        
        for word, count in word_counts.most_common(top_k):
            top_phrases.append({
                'phrase': word,
                'score': round(count / total_words, 3),
                'count': count,
                'share_neg': round(count / len(texts), 3)
            })
        
        return top_phrases
    
    def generate_insights(
        self,
        top_phrases: List[Dict[str, Any]],
        negative_reviews: List[Dict[str, Any]],
        scores: List[float],
        recency_cutoffs: List[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable insights from negative phrases.
        
        Args:
            top_phrases: Top negative phrases
            negative_reviews: Negative reviews
            scores: Sentiment scores
            recency_cutoffs: Recency cutoff days
            
        Returns:
            List of actionable insights
        """
        if recency_cutoffs is None:
            recency_cutoffs = [90, 365]
        
        insights = []
        total_neg = len(negative_reviews)
        
        for i, phrase_data in enumerate(top_phrases[:5]):  # Top 5 insights
            phrase = phrase_data['phrase']
            count = phrase_data['count']
            share_neg = phrase_data['share_neg']
            
            # Calculate severity
            severity = self._calculate_severity(phrase, negative_reviews, scores, recency_cutoffs)
            
            # Map phrase to area and action
            area, action = self._map_phrase_to_action(phrase)
            
            # Generate insight
            insight = {
                'priority': i + 1,
                'area': area,
                'issue': phrase,
                'why': f"{share_neg:.0%} negative sentiment; strong negative sentiment; recent reviews",
                'action': action,
                'impact': 'high' if severity > 0.5 else 'medium' if severity > 0.2 else 'low'
            }
            
            insights.append(insight)
        
        return insights
    
    def _calculate_severity(
        self, 
        phrase: str, 
        negative_reviews: List[Dict[str, Any]], 
        scores: List[float],
        recency_cutoffs: List[int]
    ) -> float:
        """Calculate severity score for a phrase."""
        # Frequency
        freq = sum(1 for review in negative_reviews if phrase in str(review).lower()) / len(negative_reviews)
        
        # Strength (average absolute sentiment score)
        phrase_reviews = [review for review in negative_reviews if phrase in str(review).lower()]
        if phrase_reviews:
            strength = sum(abs(review.get('sentiment_score', 0)) for review in phrase_reviews) / len(phrase_reviews)
        else:
            strength = 0.0
        
        # Recency weight
        recency_weight = self._calculate_recency_weight(phrase_reviews, recency_cutoffs)
        
        return freq * strength * recency_weight
    
    def _calculate_recency_weight(
        self, 
        reviews: List[Dict[str, Any]], 
        recency_cutoffs: List[int]
    ) -> float:
        """Calculate recency weight for reviews."""
        if not reviews:
            return 1.0
        
        now = datetime.now()
        weights = []
        
        for review in reviews:
            updated = review.get('updated')
            if not updated:
                weights.append(1.0)
                continue
            
            try:
                # Parse date
                if isinstance(updated, str):
                    review_date = date_parser.parse(updated)
                else:
                    review_date = updated
                
                # Calculate days ago
                days_ago = (now - review_date).days
                
                # Apply recency weight
                if days_ago <= recency_cutoffs[0]:
                    weight = 1.0
                elif days_ago <= recency_cutoffs[1]:
                    weight = 0.7
                else:
                    weight = 0.5
                
                weights.append(weight)
                
            except Exception:
                weights.append(1.0)
        
        return sum(weights) / len(weights) if weights else 1.0
    
    def _map_phrase_to_action(self, phrase: str) -> Tuple[str, str]:
        """Map phrase to area and action."""
        phrase_lower = phrase.lower()
        
        # Check for exact matches first
        for key, mapping in self.phrase_mappings.items():
            if key in phrase_lower:
                return mapping['area'], mapping['action']
        
        # Default mapping
        return 'General', 'Investigate the issue, gather additional information'


# Global service instance
insights_service = InsightsService()
