"""Tests for ISA Registry module."""
import pytest
from backend.datasources.isa_registry import (
    RATIFIED_EXTENSIONS,
    validate_extension,
    get_extension_info,
    suggest_extensions,
    filter_extensions_by_category,
)


def test_ratified_extensions_not_empty():
    """Test that RATIFIED_EXTENSIONS is not empty."""
    assert len(RATIFIED_EXTENSIONS) > 0
    assert "Zicbom" in RATIFIED_EXTENSIONS


def test_validate_extension_valid():
    """Test validate_extension with valid extensions."""
    assert validate_extension("Zicbom") is True
    assert validate_extension("V") is True
    assert validate_extension("Zba") is True


def test_validate_extension_invalid():
    """Test validate_extension with invalid extensions."""
    assert validate_extension("InvalidExt") is False
    assert validate_extension("") is False


def test_get_extension_info_valid():
    """Test get_extension_info with valid extension."""
    info = get_extension_info("Zicbom")
    assert info["name"] == "Zicbom"
    assert info["ratified"] is True
    assert info["category"] == "cache"


def test_get_extension_info_invalid():
    """Test get_extension_info with invalid extension."""
    info = get_extension_info("Invalid")
    assert info["ratified"] is False
    assert info["category"] == "unknown"


def test_suggest_extensions():
    """Test suggest_extensions with prefix."""
    suggestions = suggest_extensions("Zic")
    assert len(suggestions) > 0
    assert all(s.startswith("Zic") for s in suggestions)


def test_filter_extensions_by_category():
    """Test filter_extensions_by_category."""
    vector_exts = filter_extensions_by_category("vector")
    assert "V" in vector_exts
    assert "Zvbb" in vector_exts
    
    crypto_exts = filter_extensions_by_category("crypto")
    assert "Zkt" in crypto_exts
