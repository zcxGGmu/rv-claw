import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def sample_case_data():
    return {
        "case_id": "test-case-001",
        "target_repo": "linux",
        "current_stage": "explore",
        "input_context": {"arch": "RV64I"},
    }
