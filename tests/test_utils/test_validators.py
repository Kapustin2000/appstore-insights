"""
Tests for validation utilities.
"""
import pytest
from app.utils.validators import clean_app_id, validate_country_code
from app.core.exceptions import ValidationError


class TestCleanAppId:
    """Test app ID cleaning functionality."""
    
    def test_clean_app_id_with_prefix(self):
        """Test cleaning app ID with 'id' prefix."""
        result = clean_app_id("id1566419183")
        assert result == "1566419183"
    
    def test_clean_app_id_without_prefix(self):
        """Test cleaning app ID without prefix."""
        result = clean_app_id("1566419183")
        assert result == "1566419183"
    
    def test_clean_app_id_case_insensitive(self):
        """Test cleaning app ID with case insensitive prefix."""
        result = clean_app_id("ID1566419183")
        assert result == "1566419183"
    
    def test_clean_app_id_empty(self):
        """Test cleaning empty app ID."""
        with pytest.raises(ValidationError):
            clean_app_id("")
    
    def test_clean_app_id_invalid_format(self):
        """Test cleaning invalid app ID format."""
        with pytest.raises(ValidationError):
            clean_app_id("invalid")
    
    def test_clean_app_id_too_short(self):
        """Test cleaning app ID that's too short."""
        with pytest.raises(ValidationError):
            clean_app_id("123")
    
    def test_clean_app_id_too_long(self):
        """Test cleaning app ID that's too long."""
        with pytest.raises(ValidationError):
            clean_app_id("12345678901")


class TestValidateCountryCode:
    """Test country code validation functionality."""
    
    def test_validate_country_code_valid(self):
        """Test validating valid country code."""
        result = validate_country_code("us")
        assert result == "us"
    
    def test_validate_country_code_uppercase(self):
        """Test validating uppercase country code."""
        result = validate_country_code("US")
        assert result == "us"
    
    def test_validate_country_code_empty(self):
        """Test validating empty country code."""
        with pytest.raises(ValidationError):
            validate_country_code("")
    
    def test_validate_country_code_wrong_length(self):
        """Test validating country code with wrong length."""
        with pytest.raises(ValidationError):
            validate_country_code("usa")
    
    def test_validate_country_code_non_alpha(self):
        """Test validating country code with non-alpha characters."""
        with pytest.raises(ValidationError):
            validate_country_code("u1")
