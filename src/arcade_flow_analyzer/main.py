#!/usr/bin/env python3
"""
Arcade Flow Analyzer - Main Module
=================================

Main orchestration module for the Arcade Flow Analyzer.
This module coordinates the flow analysis workflow using modular components.

Author: Professional Interview Solution
Date: September 2024
"""

import json
import logging

from .config import Config, get_config
from .parser import FlowParser
from .analyzer import AIAnalyzer
from .reporter import ReportGenerator
from .behavioral_analyzer import BehavioralAnalyzer

logger = logging.getLogger(__name__)


def main():
    """
    Main execution function.

    Orchestrates the complete flow analysis workflow including:
    1. Configuration validation and setup
    2. Flow data loading and parsing
    3. AI-powered analysis
    4. Social media image generation
    5. Comprehensive report generation

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Initialize and validate configuration
        config = get_config()
        config.validate()
        config.setup_logging()

        logger.info("Starting Arcade Flow Analysis...")

        # Optional: Display configuration info for debugging
        if logger.isEnabledFor(logging.DEBUG):
            config.display_info()

        # Load flow data
        logger.info(f"Loading flow data from {config.FLOW_FILE}")
        with open(config.FLOW_FILE, "r") as f:
            flow_data = json.load(f)

        # Initialize components
        parser = FlowParser(flow_data)
        analyzer = AIAnalyzer()
        reporter = ReportGenerator()
        behavioral_analyzer = BehavioralAnalyzer(flow_data)

        # Extract and analyze data
        logger.info("Extracting user interactions...")
        interactions = parser.extract_user_interactions()
        flow_summary = parser.get_enhanced_flow_summary()
        journey_analysis = parser.analyze_user_journey()

        # Extract enhanced content
        logger.info("Extracting chapter and video content...")
        chapters = parser.extract_chapter_content()
        videos = parser.extract_video_content()
        logger.info(f"Found {len(chapters)} chapters and {len(videos)} video segments")

        # Extract company information for brand-aware image generation
        logger.info("Extracting company branding information...")
        company_info = parser.extract_company_info()
        if company_info.get("name"):
            logger.info(f"Detected company: {company_info['name']}")
        else:
            logger.info("No specific company branding detected, using generic styling")

        # Extract flow context for dynamic image generation
        logger.info("Analyzing flow context for dynamic content generation...")
        flow_context = parser.extract_flow_context()
        logger.info(f"Flow analysis: {flow_context['primary_action']} {flow_context['primary_object'] or ''} (type: {flow_context['flow_type']}, confidence: {flow_context['context_confidence']:.1f})")

        logger.info(f"Found {len(interactions)} user interactions")

        # Extract screenshots for visual analysis
        logger.info("Extracting screenshots for visual analysis...")
        screenshots = parser.extract_screenshots()
        logger.info(f"Found {len(screenshots)} screenshots")

        # Visual analysis with GPT-4 Vision
        logger.info("Performing visual analysis with GPT-4 Vision...")
        visual_analysis = analyzer.analyze_screenshots(screenshots, interactions)

        # AI-powered text analysis (enhanced with visual context)
        logger.info("Performing comprehensive AI analysis...")
        analysis = analyzer.analyze_user_intent(interactions, flow_summary, visual_analysis)

        # Behavioral analytics
        logger.info("Performing behavioral analytics...")
        behavioral_analysis = behavioral_analyzer.analyze_user_behavior()

        # Generate social media image with dynamic flow context and company branding
        logger.info("Generating social media image with dynamic flow context...")
        image_path = analyzer.generate_social_media_image(flow_summary, analysis, visual_analysis, company_info, flow_context)

        # Generate final report
        logger.info("Generating comprehensive report...")
        report_path = reporter.generate_markdown_report(
            flow_summary, interactions, analysis, journey_analysis, image_path, visual_analysis, behavioral_analysis, chapters, videos
        )

        logger.info(f"Analysis complete! Report saved to: {report_path}")

        # Get cost summary for optimization insights
        cost_summary = analyzer.get_cost_summary()

        # Print summary to console
        _print_completion_summary(flow_summary, interactions, report_path, image_path, cost_summary)

        return 0

    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
        print(f"\nERROR: File not found: {e}")
        print("Make sure the Flow.json file is in the data/raw/ directory")
        return 1

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nERROR: Configuration error: {e}")
        print("Check your .env file and ensure all required variables are set")
        return 1

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print(f"\nERROR: Analysis failed: {e}")
        return 1


def _print_completion_summary(
    flow_summary: dict, interactions: list, report_path: str, image_path: str = None, cost_summary: dict = None
) -> None:
    """
    Print a formatted completion summary to the console.

    Args:
        flow_summary: Flow metadata summary
        interactions: List of user interactions
        report_path: Path to the generated report
        image_path: Optional path to generated image
        cost_summary: Optional API cost summary for optimization insights
    """
    print("\n" + "=" * 60)
    print("ARCADE FLOW ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Flow Analyzed: {flow_summary.get('name', 'Unknown')}")
    print(f"User Interactions: {len(interactions)}")
    print(f"Report Generated: {report_path}")
    if image_path:
        print(f"Social Media Image: {image_path}")

    # Display cost optimization information
    if cost_summary:
        print("\nCOST OPTIMIZATION SUMMARY")
        print("-" * 40)
        print(f"Total API Cost: ${cost_summary['total_cost']:.4f}")
        if cost_summary['estimated_savings'] > 0:
            print(f"Estimated Savings: ${cost_summary['estimated_savings']:.4f}")
        print("Model Usage:")
        for model, usage in cost_summary['model_breakdown'].items():
            print(f"  {model}: {usage['calls']} calls, {usage['tokens']} tokens, ${usage['cost']:.4f}")

    print("=" * 60)


if __name__ == "__main__":
    exit(main())
