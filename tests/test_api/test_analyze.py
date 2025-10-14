"""
Tests for analyze endpoint.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestAnalyzeEndpoint:
    """Test cases for the analyze endpoint."""
    
    def test_analyze_endpoint_success(self):
        """Test successful analysis with real app data."""
        response = client.post("/app/analyze", json={
            "app_id": "1459969523",
            "country": "us",
            "review_limit": 10,
            "sentiment_model": "vader",
            "top_k_phrases": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert "meta" in data
        assert "sentiment_overview" in data
        assert "top_negative_phrases" in data
        assert "insights" in data
        assert "debug" in data
        
        # Check status
        assert data["status"] == "ok"
        
        # Check meta
        assert data["meta"]["app_id"] == "1459969523"
        assert data["meta"]["country"] == "us"
        assert data["meta"]["analyzed"] > 0
        assert "processing_time_ms" in data["meta"]
        
        # Check sentiment overview
        sentiment = data["sentiment_overview"]
        assert "pos" in sentiment
        assert "neu" in sentiment
        assert "neg" in sentiment
        assert "mean_star" in sentiment
        
        # Sentiment proportions should sum to approximately 1.0
        total_sentiment = sentiment["pos"] + sentiment["neu"] + sentiment["neg"]
        assert abs(total_sentiment - 1.0) < 0.1
        
        # Check debug info
        debug = data["debug"]
        assert debug["model"] == "vader"
        assert "thresholds" in debug
        assert debug["thresholds"]["neg"] == -0.2
        assert debug["thresholds"]["pos"] == 0.2
    
    def test_analyze_endpoint_with_reviews_override(self):
        """Test analysis with provided reviews data."""
        mock_reviews = [
            {
                "reviewId": "1",
                "rating": 1,
                "title": "Terrible app",
                "content": "Too many ads and crashes constantly",
                "updated": "2024-01-01T00:00:00Z"
            },
            {
                "reviewId": "2", 
                "rating": 5,
                "title": "Great app",
                "content": "Love it, works perfectly",
                "updated": "2024-01-02T00:00:00Z"
            }
        ]
        
        response = client.post("/app/analyze", json={
            "app_id": "123456789",
            "country": "us",
            "reviews_override": mock_reviews,
            "sentiment_model": "vader",
            "top_k_phrases": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should analyze the provided reviews
        assert data["meta"]["analyzed"] == 2
        
        # Should have mixed sentiment
        sentiment = data["sentiment_overview"]
        assert sentiment["pos"] > 0
        assert sentiment["neg"] > 0
    
    def test_analyze_endpoint_invalid_app_id(self):
        """Test analysis with invalid app ID."""
        response = client.post("/app/analyze", json={
            "app_id": "invalid",
            "country": "us",
            "review_limit": 10
        })
        
        assert response.status_code == 502  # iTunes API error for invalid app
    
    def test_analyze_endpoint_invalid_country(self):
        """Test analysis with invalid country code."""
        response = client.post("/app/analyze", json={
            "app_id": "1459969523",
            "country": "invalid",
            "review_limit": 10
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_endpoint_custom_parameters(self):
        """Test analysis with custom parameters."""
        response = client.post("/app/analyze", json={
            "app_id": "1459969523",
            "country": "us",
            "review_limit": 5,
            "sentiment_model": "vader",
            "ngram_range": [1, 3],
            "min_df": 1,
            "top_k_phrases": 3,
            "weights": {"text": 0.7, "stars": 0.3},
            "recency_cutoffs_days": [30, 180]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that custom parameters are reflected
        assert data["debug"]["model"] == "vader"
        assert data["meta"]["analyzed"] <= 5
        assert len(data["top_negative_phrases"]) <= 3
    
    def test_analyze_endpoint_no_reviews_found(self):
        """Test analysis when no reviews are found."""
        # Use a non-existent app ID that won't have reviews
        response = client.post("/app/analyze", json={
            "app_id": "999999999999",
            "country": "us",
            "review_limit": 10
        })
        
        # Should return 502 for iTunes API error
        assert response.status_code == 502
