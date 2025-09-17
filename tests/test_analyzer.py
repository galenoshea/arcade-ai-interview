"""
Unit tests for the AIAnalyzer module.
"""

import json
import pytest
from unittest.mock import patch, Mock, mock_open
from arcade_flow_analyzer.analyzer import AIAnalyzer


class TestAIAnalyzer:
    """Test cases for the AIAnalyzer class."""

    @patch("arcade_flow_analyzer.analyzer.get_config")
    def test_init_with_api_key(self, mock_get_config):
        """Test AIAnalyzer initialization with provided API key."""
        mock_config = Mock()
        mock_config.OPENAI_API_KEY = "config-key"
        mock_get_config.return_value = mock_config

        with patch("arcade_flow_analyzer.analyzer.openai.OpenAI") as mock_openai:
            analyzer = AIAnalyzer("provided-key")
            mock_openai.assert_called_once_with(api_key="provided-key")

    @patch("arcade_flow_analyzer.analyzer.get_config")
    def test_init_without_api_key(self, mock_get_config):
        """Test AIAnalyzer initialization using config API key."""
        mock_config = Mock()
        mock_config.OPENAI_API_KEY = "config-key"
        mock_get_config.return_value = mock_config

        with patch("arcade_flow_analyzer.analyzer.openai.OpenAI") as mock_openai:
            analyzer = AIAnalyzer()
            mock_openai.assert_called_once_with(api_key="config-key")

    @patch("arcade_flow_analyzer.analyzer.get_config")
    def test_init_no_api_key_error(self, mock_get_config):
        """Test AIAnalyzer initialization with no API key raises error."""
        mock_config = Mock()
        mock_config.OPENAI_API_KEY = None
        mock_get_config.return_value = mock_config

        with pytest.raises(ValueError, match="OpenAI API key is required"):
            AIAnalyzer()

    @patch("arcade_flow_analyzer.analyzer.get_config")
    @patch("arcade_flow_analyzer.analyzer.openai.OpenAI")
    @patch("arcade_flow_analyzer.analyzer.CacheManager")
    def test_analyze_user_intent_from_cache(
        self, mock_cache_manager, mock_openai, mock_get_config
    ):
        """Test user intent analysis using cached results."""
        # Setup mocks
        mock_config = Mock()
        mock_config.OPENAI_API_KEY = "test-key"
        mock_get_config.return_value = mock_config

        mock_cache = Mock()
        cached_result = {
            "summary": "Cached summary",
            "user_goal": "Cached goal",
            "key_insights": "Cached insights",
        }
        mock_cache.get.return_value = cached_result
        mock_cache_manager.return_value = mock_cache

        analyzer = AIAnalyzer()

        # Test with cache hit
        result = analyzer.analyze_user_intent(
            [{"description": "test"}], {"name": "test flow"}
        )

        assert result == cached_result
        mock_cache.get.assert_called_once()
        # Should not call OpenAI API when using cache
        mock_openai.return_value.chat.completions.create.assert_not_called()

    @patch("arcade_flow_analyzer.analyzer.get_config")
    @patch("arcade_flow_analyzer.analyzer.openai.OpenAI")
    @patch("arcade_flow_analyzer.analyzer.CacheManager")
    def test_analyze_user_intent_api_call(
        self, mock_cache_manager, mock_openai, mock_get_config
    ):
        """Test user intent analysis with API call."""
        # Setup mocks
        mock_config = Mock()
        mock_config.OPENAI_API_KEY = "test-key"
        mock_get_config.return_value = mock_config

        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss
        mock_cache_manager.return_value = mock_cache

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[
            0
        ].message.content = json.dumps({
            "summary": "User completed a test workflow",
            "user_goal": "Test the application",
            "key_insights": "Good user experience"
        })
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 150
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        analyzer = AIAnalyzer()

        # Test with cache miss
        result = analyzer.analyze_user_intent(
            [{"description": "test interaction", "page_title": "test page"}],
            {"name": "test flow", "total_steps": 1, "use_case": "testing"},
        )

        # Verify API was called
        mock_openai.return_value.chat.completions.create.assert_called_once()

        # Verify result structure
        assert "summary" in result
        assert "user_goal" in result
        assert "key_insights" in result

        # Verify cache was set
        mock_cache.set.assert_called_once()

    def test_create_analysis_prompt(self, sample_interactions, sample_flow_summary):
        """Test analysis prompt creation."""
        with patch("arcade_flow_analyzer.analyzer.get_config"):
            with patch("arcade_flow_analyzer.analyzer.openai.OpenAI"):
                with patch("arcade_flow_analyzer.analyzer.CacheManager"):
                    analyzer = AIAnalyzer("test-key")

                    prompt = analyzer._create_analysis_prompt(
                        sample_interactions, sample_flow_summary
                    )

                    assert "Test Flow" in prompt
                    assert "Click the test button" in prompt
                    assert "Test Page" in prompt
                    assert "user flow" in prompt.lower()
                    assert "interactions" in prompt.lower()
                    assert "analysis" in prompt.lower()

    def test_structured_response_format(self):
        """Test that analyzer uses structured JSON schema format."""
        with patch("arcade_flow_analyzer.analyzer.get_config"):
            with patch("arcade_flow_analyzer.analyzer.openai.OpenAI"):
                with patch("arcade_flow_analyzer.analyzer.CacheManager"):
                    analyzer = AIAnalyzer("test-key")

                    # Verify that the analyzer has the ANALYSIS_SCHEMA
                    assert hasattr(analyzer, 'ANALYSIS_SCHEMA')
                    assert analyzer.ANALYSIS_SCHEMA is not None

                    # Check that the schema has the required structure
                    schema = analyzer.ANALYSIS_SCHEMA
                    assert "type" in schema
                    assert "properties" in schema

                    # Verify required fields are in the schema
                    properties = schema["properties"]
                    assert "summary" in properties
                    assert "user_goal" in properties
                    assert "key_insights" in properties

    @patch("arcade_flow_analyzer.analyzer.get_config")
    @patch("arcade_flow_analyzer.analyzer.openai.OpenAI")
    @patch("arcade_flow_analyzer.analyzer.CacheManager")
    def test_analyze_user_intent_api_error(
        self, mock_cache_manager, mock_openai, mock_get_config
    ):
        """Test user intent analysis with API error."""
        # Setup mocks
        mock_config = Mock()
        mock_config.OPENAI_API_KEY = "test-key"
        mock_get_config.return_value = mock_config

        mock_cache = Mock()
        mock_cache.get.return_value = None  # Cache miss
        mock_cache_manager.return_value = mock_cache

        # Mock API error
        mock_openai.return_value.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        analyzer = AIAnalyzer()

        # Test error handling
        result = analyzer.analyze_user_intent(
            [{"description": "test", "page_title": "test page"}], {"name": "test flow"}
        )

        # Should return error response
        assert "Unable to determine user goal due to API error" in result["user_goal"]
        assert "AI analysis temporarily unavailable" in result["key_insights"]

    @patch("arcade_flow_analyzer.analyzer.requests.get")
    def test_download_and_save_image(self, mock_requests_get):
        """Test image download and save functionality."""
        with patch("arcade_flow_analyzer.analyzer.get_config") as mock_get_config:
            with patch("arcade_flow_analyzer.analyzer.openai.OpenAI"):
                with patch("arcade_flow_analyzer.analyzer.CacheManager"):
                    # Setup config mock
                    from pathlib import Path
                    mock_config = Mock()
                    mock_config.OPENAI_API_KEY = "test-key"
                    mock_config.RESULTS_DIR = Path("/tmp/test_results")
                    mock_get_config.return_value = mock_config

                    # Setup requests mock
                    mock_response = Mock()
                    mock_response.content = b"fake image data"
                    mock_response.raise_for_status = Mock()
                    mock_requests_get.return_value = mock_response

                    # Setup file operations
                    with patch("builtins.open", mock_open()) as mock_file:
                        analyzer = AIAnalyzer("test-key")
                        result = analyzer._download_and_save_image(
                            "https://example.com/image.png", "test_image.png"
                        )

                        # Verify download was attempted
                        mock_requests_get.assert_called_once_with(
                            "https://example.com/image.png"
                        )

                        # Verify file was written
                        mock_file.assert_called_once()
                        mock_file().write.assert_called_once_with(b"fake image data")

    def test_create_image_prompt(self, sample_flow_summary, sample_analysis):
        """Test image generation prompt creation."""
        with patch("arcade_flow_analyzer.analyzer.get_config"):
            with patch("arcade_flow_analyzer.analyzer.openai.OpenAI"):
                with patch("arcade_flow_analyzer.analyzer.CacheManager"):
                    analyzer = AIAnalyzer("test-key")

                    # Pass None for optional parameters to match new signature
                    prompt = analyzer._create_image_prompt(
                        sample_flow_summary, sample_analysis, None, None, None
                    )

                    assert "professional social media image" in prompt
                    assert "Made Easy" in prompt
                    assert "CONTEXT REQUIREMENTS" in prompt
                    assert "TEXT OVERLAY REQUIREMENTS" in prompt
