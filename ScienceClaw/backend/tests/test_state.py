"""Tests for PipelineState model."""
import pytest
from backend.pipeline.state import PipelineState


def test_pipeline_state_default_construction():
    """Test PipelineState with default values."""
    state = PipelineState(case_id="test-123", target_repo="linux")
    
    assert state.case_id == "test-123"
    assert state.target_repo == "linux"
    assert state.current_stage == "explore"
    assert state.review_iterations == 0
    assert state.max_review_iterations == 3


def test_pipeline_state_serialization():
    """Test PipelineState serialization to dict."""
    state = PipelineState(
        case_id="test-456",
        target_repo="qemu",
        current_stage="review",
        review_iterations=2,
    )
    
    data = state.model_dump()
    assert data["case_id"] == "test-456"
    assert data["target_repo"] == "qemu"
    assert data["current_stage"] == "review"
    assert data["review_iterations"] == 2


def test_pipeline_state_deserialization():
    """Test PipelineState deserialization from dict."""
    data = {
        "case_id": "test-789",
        "target_repo": "opensbi",
        "current_stage": "test",
        "input_context": {"key": "value"},
        "review_iterations": 1,
    }
    
    state = PipelineState.model_validate(data)
    assert state.case_id == "test-789"
    assert state.target_repo == "opensbi"
    assert state.current_stage == "test"
    assert state.input_context == {"key": "value"}


def test_pipeline_state_missing_optional_fields():
    """Test PipelineState with missing optional fields."""
    data = {
        "case_id": "test-minimal",
        "target_repo": "linux",
    }
    
    state = PipelineState.model_validate(data)
    assert state.case_id == "test-minimal"
    assert state.target_repo == "linux"
    assert state.current_stage == "explore"  # default
    assert state.exploration_result_ref is None


def test_pipeline_state_cost_tracking():
    """Test PipelineState cost tracking fields."""
    state = PipelineState(
        case_id="test-cost",
        target_repo="linux",
        total_input_tokens=1000,
        total_output_tokens=500,
        estimated_cost_usd=0.015,
    )
    
    assert state.total_input_tokens == 1000
    assert state.total_output_tokens == 500
    assert state.estimated_cost_usd == 0.015
