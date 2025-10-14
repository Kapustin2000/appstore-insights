"""
Tests for app service.
"""
import pytest
from unittest.mock import patch, Mock
from app.services.app_service import fetch_app_info, fetch_reviews_paged


class TestFetchAppInfo:
    """Test app info fetching functionality."""
    
    @patch('app.services.app_service.requests.get')
    def test_fetch_app_info_success(self, mock_get):
        """Test successful app info fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "resultCount": 1,
            "results": [{
                "trackId": 1566419183,
                "trackName": "Test App",
                "bundleId": "com.test.app",
                "version": "1.0.0",
                "price": 0.0,
                "formattedPrice": "Free",
                "description": "Test app description",
                "averageUserRating": 4.5,
                "userRatingCount": 100,
                "averageUserRatingForCurrentVersion": 4.5,
                "userRatingCountForCurrentVersion": 50,
                "releaseDate": "2023-01-01T00:00:00Z",
                "currentVersionReleaseDate": "2023-01-01T00:00:00Z",
                "releaseNotes": "Initial release",
                "artistName": "Test Developer",
                "artistId": 123456,
                "sellerName": "Test Developer",
                "primaryGenreName": "Games",
                "genres": ["Games"],
                "genreIds": ["6014"],
                "contentAdvisoryRating": "4+",
                "minimumOsVersion": "13.0",
                "fileSizeBytes": "1000000",
                "languageCodesISO2A": ["EN"],
                "screenshotUrls": ["https://example.com/screenshot.png"],
                "ipadScreenshotUrls": [],
                "artworkUrl60": "https://example.com/icon60.png",
                "artworkUrl100": "https://example.com/icon100.png",
                "artworkUrl512": "https://example.com/icon512.png",
                "trackViewUrl": "https://apps.apple.com/app/test-app/id1566419183",
                "artistViewUrl": "https://apps.apple.com/developer/test-developer/id123456",
                "sellerUrl": "https://example.com"
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test
        result = fetch_app_info("1566419183", "us")
        
        # Assertions
        assert result["status"] == "success"
        assert result["details"]["appId"] == 1566419183
        assert result["details"]["name"] == "Test App"
    
    @patch('app.services.app_service.requests.get')
    def test_fetch_app_info_not_found(self, mock_get):
        """Test app info fetching when app not found."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"resultCount": 0, "results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test
        result = fetch_app_info("999999999", "us")
        
        # Assertions
        assert result["status"] == "not_found"
        assert result["details"] is None


class TestFetchReviewsPaged:
    """Test reviews fetching functionality."""
    
    @patch('app.services.app_service.requests.get')
    def test_fetch_reviews_paged_success(self, mock_get):
        """Test successful reviews fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "feed": {
                "entry": [
                    {
                        "id": {"label": "review1"},
                        "im:rating": {"label": "5"},
                        "title": {"label": "Great app!"},
                        "content": {"label": "Love this app"},
                        "updated": {"label": "2023-01-01T00:00:00Z"},
                        "im:version": {"label": "1.0.0"},
                        "author": {"name": {"label": "User1"}}
                    }
                ],
                "link": []
            }
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test
        result = fetch_reviews_paged("1566419183", "us", limit=1)
        
        # Assertions
        assert result["status"] == "success"
        assert len(result["items"]) == 1
        assert result["items"][0]["reviewId"] == "review1"
        assert result["items"][0]["rating"] == 5
