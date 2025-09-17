"""
Unit tests for the FlowParser module.
"""

import pytest
from arcade_flow_analyzer.parser import FlowParser


class TestFlowParser:
    """Test cases for the FlowParser class."""

    def test_init(self, sample_flow_data):
        """Test FlowParser initialization."""
        parser = FlowParser(sample_flow_data)

        assert parser.flow_data == sample_flow_data
        assert parser.flow_name == "Test Flow"
        assert len(parser.steps) == 2
        assert len(parser.captured_events) == 1

    def test_init_with_missing_name(self, sample_flow_data):
        """Test FlowParser initialization with missing name."""
        del sample_flow_data["name"]
        parser = FlowParser(sample_flow_data)

        assert parser.flow_name == "Unknown Flow"

    def test_extract_user_interactions(self, sample_flow_data):
        """Test extraction of user interactions."""
        parser = FlowParser(sample_flow_data)
        interactions = parser.extract_user_interactions()

        assert len(interactions) == 1
        interaction = interactions[0]

        assert interaction["step_id"] == "test-step-1"
        assert interaction["action_type"] == "click"
        assert interaction["description"] == "Click the test button"
        assert interaction["url"] == "https://example.com"
        assert interaction["page_title"] == "Test Page"
        assert interaction["element_type"] == "button"
        assert interaction["element_text"] == "Test Button"
        assert interaction["coordinates"]["x"] == 0.5
        assert interaction["coordinates"]["y"] == 0.5

    def test_extract_user_interactions_no_hotspots(self, sample_flow_data):
        """Test extraction when steps have no hotspots."""
        # Remove hotspots from all steps
        for step in sample_flow_data["steps"]:
            if "hotspots" in step:
                del step["hotspots"]

        parser = FlowParser(sample_flow_data)
        interactions = parser.extract_user_interactions()

        assert len(interactions) == 0

    def test_get_flow_summary(self, sample_flow_data):
        """Test flow summary generation."""
        parser = FlowParser(sample_flow_data)
        summary = parser.get_flow_summary()

        assert summary["name"] == "Test Flow"
        assert summary["description"] == "A test flow for unit testing"
        assert summary["use_case"] == "testing"
        assert summary["total_steps"] == 2
        assert summary["has_ai_processing"] is True
        assert summary["schema_version"] == "1.1.0"

    def test_analyze_user_journey(self, sample_flow_data):
        """Test user journey analysis."""
        parser = FlowParser(sample_flow_data)
        journey = parser.analyze_user_journey()

        assert journey["total_interactions"] == 1
        assert journey["start_url"] == "https://example.com"
        assert journey["end_url"] == "https://example.com"
        assert len(journey["page_transitions"]) == 1
        assert len(journey["key_actions"]) == 1

    def test_analyze_user_journey_empty(self):
        """Test user journey analysis with no interactions."""
        empty_flow_data = {"name": "Empty Flow", "steps": [], "capturedEvents": []}

        parser = FlowParser(empty_flow_data)
        journey = parser.analyze_user_journey()

        assert journey["total_interactions"] == 0
        assert journey["start_url"] == ""
        assert journey["end_url"] == ""
        assert len(journey["page_transitions"]) == 0
        assert len(journey["key_actions"]) == 0

    def test_key_actions_detection(self, sample_flow_data):
        """Test detection of key actions based on keywords."""
        # Modify the hotspot label to include key action keywords
        sample_flow_data["steps"][0]["hotspots"][0]["label"] = "Add to cart"

        parser = FlowParser(sample_flow_data)
        journey = parser.analyze_user_journey()

        assert len(journey["key_actions"]) == 1
        key_action = journey["key_actions"][0]
        assert key_action["action"] == "Add to cart"
        assert key_action["url"] == "https://example.com"
        assert key_action["element"] == "Test Button"
