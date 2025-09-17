"""
Unit tests for the ReportGenerator module.
"""

import pytest
from unittest.mock import patch, Mock, mock_open
from arcade_flow_analyzer.reporter import ReportGenerator


class TestReportGenerator:
    """Test cases for the ReportGenerator class."""

    @patch("arcade_flow_analyzer.reporter.get_config")
    def test_init(self, mock_get_config, temp_results_dir):
        """Test ReportGenerator initialization."""
        mock_config = Mock()
        mock_config.RESULTS_DIR = temp_results_dir
        mock_get_config.return_value = mock_config

        reporter = ReportGenerator()

        assert reporter.output_dir == temp_results_dir
        assert temp_results_dir.exists()

    def test_init_with_custom_dir(self, temp_results_dir):
        """Test ReportGenerator initialization with custom directory."""
        with patch("arcade_flow_analyzer.reporter.get_config"):
            reporter = ReportGenerator(temp_results_dir)
            assert reporter.output_dir == temp_results_dir

    @patch("arcade_flow_analyzer.reporter.get_config")
    def test_generate_markdown_report(
        self,
        mock_get_config,
        temp_results_dir,
        sample_flow_summary,
        sample_interactions,
        sample_analysis,
        sample_journey_analysis,
    ):
        """Test markdown report generation."""
        mock_config = Mock()
        mock_config.RESULTS_DIR = temp_results_dir
        mock_get_config.return_value = mock_config

        reporter = ReportGenerator()

        with patch("builtins.open", mock_open()) as mock_file:
            report_path = reporter.generate_markdown_report(
                sample_flow_summary,
                sample_interactions,
                sample_analysis,
                sample_journey_analysis,
                "test_image.png",
            )

            # Verify file was written
            mock_file.assert_called_once()
            written_content = mock_file().write.call_args[0][0]

            # Verify report content
            assert "# Arcade Flow Analysis Report" in written_content
            assert "Test Flow" in written_content
            assert "Click the test button" in written_content
            assert "Test the application functionality" in written_content
            assert "test_image.png" in written_content

            # Verify return value
            assert str(temp_results_dir / "flow_analysis_report.md") == report_path

    def test_create_report_content_structure(
        self,
        sample_flow_summary,
        sample_interactions,
        sample_analysis,
        sample_journey_analysis,
    ):
        """Test the structure of generated report content."""
        with patch("arcade_flow_analyzer.reporter.get_config"):
            reporter = ReportGenerator()

            content = reporter._create_report_content(
                sample_flow_summary,
                sample_interactions,
                sample_analysis,
                sample_journey_analysis,
                None,  # No image
            )

            # Check for required sections
            required_sections = [
                "# Arcade Flow Analysis Report",
                "## Executive Summary",
                "## User Journey Analysis",
                "## User Interactions Breakdown",
                "## Page Navigation Flow",
                "## Key Insights & Analysis",
                "## Visual Design Analysis",
                "## Technical Details",
                "## Social Media Asset",
                "## Flow Reproduction Guide",
                "## Original Flow Reference",
            ]

            for section in required_sections:
                assert section in content

    def test_create_report_content_with_image(
        self,
        sample_flow_summary,
        sample_interactions,
        sample_analysis,
        sample_journey_analysis,
    ):
        """Test report content generation with social media image."""
        with patch("arcade_flow_analyzer.reporter.get_config"):
            with patch("arcade_flow_analyzer.reporter.Path") as mock_path:
                # Mock image path exists
                mock_path.return_value.exists.return_value = True

                reporter = ReportGenerator()

                content = reporter._create_report_content(
                    sample_flow_summary,
                    sample_interactions,
                    sample_analysis,
                    sample_journey_analysis,
                    "test_image.png",
                )

                assert "![Social Media Image](test_image.png)" in content
                assert "Professional social media image generated" in content

    def test_create_report_content_without_image(
        self,
        sample_flow_summary,
        sample_interactions,
        sample_analysis,
        sample_journey_analysis,
    ):
        """Test report content generation without social media image."""
        with patch("arcade_flow_analyzer.reporter.get_config"):
            reporter = ReportGenerator()

            content = reporter._create_report_content(
                sample_flow_summary,
                sample_interactions,
                sample_analysis,
                sample_journey_analysis,
                None,
            )

            assert (
                "Social media image generation was attempted but could not be completed"
                in content
            )

    def test_create_report_content_empty_interactions(
        self, sample_flow_summary, sample_analysis, sample_journey_analysis
    ):
        """Test report content generation with empty interactions."""
        with patch("arcade_flow_analyzer.reporter.get_config"):
            reporter = ReportGenerator()

            content = reporter._create_report_content(
                sample_flow_summary,
                [],  # Empty interactions
                sample_analysis,
                sample_journey_analysis,
                None,
            )

            assert "No interactions captured" in content
            assert "No reproduction steps available" in content

    @patch("arcade_flow_analyzer.reporter.get_config")
    def test_generate_summary_report(
        self,
        mock_get_config,
        temp_results_dir,
        sample_flow_summary,
        sample_interactions,
        sample_analysis,
    ):
        """Test summary report generation."""
        mock_config = Mock()
        mock_config.RESULTS_DIR = temp_results_dir
        mock_get_config.return_value = mock_config

        reporter = ReportGenerator()

        with patch("builtins.open", mock_open()) as mock_file:
            summary_path = reporter.generate_summary_report(
                sample_flow_summary, sample_interactions, sample_analysis
            )

            # Verify file was written
            mock_file.assert_called_once()
            written_content = mock_file().write.call_args[0][0]

            # Verify summary content
            assert "# Flow Analysis Summary" in written_content
            assert "Test Flow" in written_content
            assert "User Interactions: 1" in written_content
            assert "Test the application functionality" in written_content

            # Verify return value
            assert str(temp_results_dir / "flow_summary.md") == summary_path

    def test_quality_metrics_calculation(
        self,
        sample_flow_summary,
        sample_interactions,
        sample_analysis,
        sample_journey_analysis,
    ):
        """Test quality metrics calculation in report."""
        with patch("arcade_flow_analyzer.reporter.get_config"):
            reporter = ReportGenerator()

            # Test with multiple interactions (should be "Smooth")
            multiple_interactions = sample_interactions * 4  # 4 interactions

            content = reporter._create_report_content(
                sample_flow_summary,
                multiple_interactions,
                sample_analysis,
                sample_journey_analysis,
                None,
            )

            assert "User Experience:** Smooth" in content
            assert "Interaction Clarity:** High" in content
            assert "Total User Interactions:** 4" in content

    def test_page_transitions_formatting(
        self, sample_flow_summary, sample_interactions, sample_analysis
    ):
        """Test page transitions formatting in report."""
        with patch("arcade_flow_analyzer.reporter.get_config"):
            reporter = ReportGenerator()

            journey_analysis = {
                "page_transitions": [
                    {
                        "from": "",
                        "to": "https://example.com",
                        "page_title": "Home Page",
                    },
                    {
                        "from": "https://example.com",
                        "to": "https://example.com/product",
                        "page_title": "Product Page",
                    },
                ],
                "key_actions": [],
                "total_interactions": 1,
            }

            content = reporter._create_report_content(
                sample_flow_summary,
                sample_interactions,
                sample_analysis,
                journey_analysis,
                None,
            )

            assert "**Home Page**: `https://example.com`" in content
            assert "**Product Page**: `https://example.com/product`" in content
