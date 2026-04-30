"""Tests for PatchworkClient."""
import pytest
from datetime import datetime, timedelta
from backend.datasources.patchwork import PatchworkClient


def test_patchwork_client_initialization():
    """Test PatchworkClient initialization."""
    client = PatchworkClient()
    assert client.timeout == 30.0
    
    client_custom = PatchworkClient(timeout=60.0)
    assert client_custom.timeout == 60.0


def test_extract_date_iso_format():
    """Test date extraction with ISO format."""
    client = PatchworkClient()
    patch = {"date": "2024-01-15T10:30:00+00:00"}
    result = client._extract_date(patch)
    assert result is not None
    assert result.year == 2024


def test_extract_date_alternative_formats():
    """Test date extraction with various formats."""
    client = PatchworkClient()
    
    patch1 = {"date_created": "2024-01-15T10:30:00"}
    result1 = client._extract_date(patch1)
    assert result1 is not None
    
    patch2 = {"date_updated": "2024-06-20T15:45:30"}
    result2 = client._extract_date(patch2)
    assert result2 is not None


def test_extract_date_invalid():
    """Test date extraction with invalid date."""
    client = PatchworkClient()
    patch = {"date": "invalid-date"}
    result = client._extract_date(patch)
    assert result is None
