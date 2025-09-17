"""
Pytest configuration and shared fixtures for Arcade Flow Analyzer tests.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock

# Sample flow data for testing
SAMPLE_FLOW_DATA = {
    "name": "Test Flow",
    "description": "A test flow for unit testing",
    "useCase": "testing",
    "schemaVersion": "1.1.0",
    "hasUsedAI": True,
    "created": {"_seconds": 1756746380, "_nanoseconds": 124000000},
    "steps": [
        {
            "id": "test-step-1",
            "type": "IMAGE",
            "hotspots": [
                {
                    "id": "test-hotspot-1",
                    "label": "Click the test button",
                    "x": 0.5,
                    "y": 0.5,
                }
            ],
            "pageContext": {
                "url": "https://example.com",
                "title": "Test Page",
                "language": "en-US",
            },
            "clickContext": {
                "cssSelector": "button[id='test']",
                "text": "Test Button",
                "elementType": "button",
            },
        },
        {"id": "test-step-2", "type": "VIDEO", "url": "https://example.com/video.mp4"},
    ],
    "capturedEvents": [
        {"type": "click", "clickId": "test-click-1", "timeMs": 1756746383245}
    ],
}


@pytest.fixture
def sample_flow_data():
    """Provide sample flow data for testing."""
    import copy
    return copy.deepcopy(SAMPLE_FLOW_DATA)


@pytest.fixture
def sample_interactions():
    """Provide sample user interactions for testing."""
    return [
        {
            "step_id": "test-step-1",
            "action_type": "click",
            "description": "Click the test button",
            "url": "https://example.com",
            "page_title": "Test Page",
            "element_type": "button",
            "element_text": "Test Button",
            "css_selector": "button[id='test']",
            "coordinates": {"x": 0.5, "y": 0.5},
        }
    ]


@pytest.fixture
def sample_flow_summary():
    """Provide sample flow summary for testing."""
    return {
        "name": "Test Flow",
        "description": "A test flow for unit testing",
        "use_case": "testing",
        "total_steps": 2,
        "has_ai_processing": True,
        "created": {"_seconds": 1756746380, "_nanoseconds": 124000000},
        "schema_version": "1.1.0",
    }


@pytest.fixture
def sample_analysis():
    """Provide sample AI analysis results for testing."""
    return {
        "summary": "User completed a test workflow successfully.",
        "user_goal": "Test the application functionality",
        "key_insights": "- User was able to navigate easily\n- Interface was intuitive",
    }


@pytest.fixture
def sample_journey_analysis():
    """Provide sample journey analysis for testing."""
    return {
        "start_url": "https://example.com",
        "end_url": "https://example.com/completed",
        "page_transitions": [
            {"from": "", "to": "https://example.com", "page_title": "Test Page"}
        ],
        "key_actions": [
            {
                "action": "Click the test button",
                "url": "https://example.com",
                "element": "Test Button",
            }
        ],
        "total_interactions": 1,
    }


@pytest.fixture
def mock_openai_client():
    """Provide a mock OpenAI client for testing."""
    mock_client = Mock()

    # Mock chat completion response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[
        0
    ].message.content = """
    SUMMARY: User completed a test workflow successfully.
    USER_GOAL: Test the application functionality
    KEY_INSIGHTS: - User was able to navigate easily
    - Interface was intuitive
    """
    mock_client.chat.completions.create.return_value = mock_response

    # Mock image generation response
    mock_image_response = Mock()
    mock_image_response.data = [Mock()]
    mock_image_response.data[0].url = "https://example.com/image.png"
    mock_client.images.generate.return_value = mock_image_response

    return mock_client


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Provide a temporary cache directory for testing."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def temp_results_dir(tmp_path):
    """Provide a temporary results directory for testing."""
    results_dir = tmp_path / "test_results"
    results_dir.mkdir()
    return results_dir


@pytest.fixture
def mock_config(temp_cache_dir, temp_results_dir, tmp_path):
    """Provide a mock configuration for testing."""
    mock_config = Mock()
    mock_config.CACHE_DIR = temp_cache_dir
    mock_config.RESULTS_DIR = temp_results_dir
    mock_config.FLOW_FILE = tmp_path / "test_flow.json"
    mock_config.OPENAI_API_KEY = "test-api-key"
    mock_config.get_cache_ttl_seconds.return_value = 3600
    return mock_config
