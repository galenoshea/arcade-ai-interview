"""
Report Generation Module

This module contains the ReportGenerator class responsible for creating
comprehensive markdown reports from flow analysis data.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .config import get_config

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive markdown reports."""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the ReportGenerator.

        Args:
            output_dir: Optional output directory path. Uses config default if not provided.
        """
        config = get_config()
        self.output_dir = output_dir or config.RESULTS_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.config = config

    def generate_markdown_report(
        self,
        flow_summary: Dict,
        interactions: List[Dict],
        analysis: Dict,
        journey_analysis: Dict,
        image_path: Optional[str] = None,
        visual_analysis: Optional[Dict] = None,
        chapters: Optional[List[Dict]] = None,
        videos: Optional[List[Dict]] = None,
    ) -> str:
        """
        Generate a comprehensive markdown report.
        Enhanced with visual and content analysis insights.

        Args:
            flow_summary: Flow metadata summary
            interactions: List of user interactions
            analysis: AI analysis results
            journey_analysis: User journey analysis
            image_path: Optional path to generated social media image
            visual_analysis: Optional visual analysis results from GPT-4 Vision
            chapters: Optional chapter content from CHAPTER steps
            videos: Optional video content from VIDEO steps

        Returns:
            Path to the generated report file
        """
        report_content = self._create_report_content(
            flow_summary, interactions, analysis, journey_analysis, image_path, visual_analysis, chapters, videos
        )

        # Save the report
        report_path = self.output_dir / "flow_analysis_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"Generated comprehensive report: {report_path}")
        return str(report_path)

    def _create_report_content(
        self,
        flow_summary: Dict,
        interactions: List[Dict],
        analysis: Dict,
        journey_analysis: Dict,
        image_path: Optional[str],
        visual_analysis: Optional[Dict] = None,
        chapters: Optional[List[Dict]] = None,
        videos: Optional[List[Dict]] = None,
    ) -> str:
        """
        Create the markdown content for the report.
        Enhanced with visual analysis insights.

        Args:
            flow_summary: Flow metadata summary
            interactions: List of user interactions
            analysis: AI analysis results
            journey_analysis: User journey analysis
            image_path: Optional path to generated social media image
            visual_analysis: Optional visual analysis results from GPT-4 Vision

        Returns:
            Complete markdown report content
        """
        # Format timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        # Create user interactions list
        interactions_list = []
        for i, interaction in enumerate(interactions, 1):
            page_info = (
                f" (on {interaction['page_title']})"
                if interaction["page_title"]
                else ""
            )
            interactions_list.append(f"{i}. {interaction['description']}{page_info}")

        # Create page transitions
        transitions_list = []
        for transition in journey_analysis.get("page_transitions", []):
            if transition["to"]:
                transitions_list.append(
                    f"- **{transition['page_title']}**: `{transition['to']}`"
                )

        report = f"""# Arcade Flow Analysis Report

## Executive Summary

**Generated on:** {timestamp}
**Flow Name:** {flow_summary.get('name', 'Unknown Flow')}
**Analysis Type:** AI-Powered User Journey Analysis

{analysis.get('summary', 'No summary available')}

---

## User Journey Analysis

### Primary User Goal
{analysis.get('user_goal', 'User goal could not be determined')}

### Flow Metadata
- **Total Steps:** {flow_summary.get('total_steps', 0)}
- **Use Case:** {flow_summary.get('use_case', 'Not specified')}
- **AI Processing Used:** {'Yes' if flow_summary.get('has_ai_processing') else 'No'}
- **Schema Version:** {flow_summary.get('schema_version', 'Unknown')}

---

## User Interactions Breakdown

Below is a chronological list of all user interactions captured in this flow:

{chr(10).join(interactions_list) if interactions_list else "No interactions captured"}

---

## Page Navigation Flow

The user navigated through the following pages during their journey:

{chr(10).join(transitions_list) if transitions_list else "No page transitions recorded"}

---

## Key Insights & Analysis

{analysis.get('key_insights', 'No insights available')}

---

## Visual Design Analysis

{self._format_visual_analysis(visual_analysis)}


{self._format_content_analysis(chapters, videos, flow_summary)}

---

## Technical Details

### Flow Statistics
- **Total User Interactions:** {len(interactions)}
- **Unique Pages Visited:** {len(set(i['url'] for i in interactions)) if interactions else 0}
- **Journey Completion:** {'Successful' if interactions else 'Incomplete'}

### Flow Quality Metrics
- **User Experience:** {'Smooth' if len(interactions) > 3 else 'Basic'}
- **Interaction Clarity:** {'High' if all(i['description'] for i in interactions) else 'Medium'}
- **Navigation Efficiency:** {'Optimized' if len(journey_analysis.get('page_transitions', [])) <= 5 else 'Complex'}

---

## Social Media Asset
"""

        if image_path and Path(image_path).exists():
            report += f"""
![Social Media Image]({image_path})

*Professional social media image generated to represent this user flow and drive engagement.*

"""
        else:
            report += """
*Social media image generation was attempted but could not be completed.*

"""

        report += f"""---

## Flow Reproduction Guide

To reproduce this user flow:

{chr(10).join([f"{i+1}. {interaction['description']}" for i, interaction in enumerate(interactions)]) if interactions else "No reproduction steps available"}

---

## Original Flow Reference

This analysis is based on the Arcade flow recording available at:
https://app.arcade.software/share/{flow_summary.get('name', '').replace(' ', '')}

---

*Report generated using AI-powered flow analysis with OpenAI GPT-4 and DALL-E 3*
*Timestamp: {timestamp}*
"""

        return report

    def generate_summary_report(
        self, flow_summary: Dict, interactions: List[Dict], analysis: Dict
    ) -> str:
        """
        Generate a brief summary report for quick overview.

        Args:
            flow_summary: Flow metadata summary
            interactions: List of user interactions
            analysis: AI analysis results

        Returns:
            Path to the generated summary report file
        """
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        summary_content = f"""# Flow Analysis Summary

**Generated on:** {timestamp}
**Flow:** {flow_summary.get('name', 'Unknown Flow')}

## Quick Stats
- **User Interactions:** {len(interactions)}
- **Flow Steps:** {flow_summary.get('total_steps', 0)}
- **Use Case:** {flow_summary.get('use_case', 'Not specified')}

## User Goal
{analysis.get('user_goal', 'User goal could not be determined')}

## Summary
{analysis.get('summary', 'No summary available')}

---
*Generated by Arcade Flow Analyzer*
"""

        # Save the summary report
        summary_path = self.output_dir / "flow_summary.md"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_content)

        logger.info(f"Generated summary report: {summary_path}")
        return str(summary_path)

    def _format_visual_analysis(self, visual_analysis: Optional[Dict]) -> str:
        """
        Format visual analysis results for inclusion in the markdown report.

        Args:
            visual_analysis: Optional visual analysis results from GPT-4 Vision

        Returns:
            Formatted markdown content for visual analysis section
        """
        if not visual_analysis:
            return "*Visual analysis was not performed for this flow.*"

        # Extract key visual information
        app_type = visual_analysis.get('app_type', 'Unknown')
        visual_style = visual_analysis.get('visual_style', 'Unknown')
        brand_colors = visual_analysis.get('brand_colors', [])
        ui_patterns = visual_analysis.get('ui_patterns', [])
        design_insights = visual_analysis.get('design_insights', [])
        visual_summary = visual_analysis.get('visual_summary', '')

        content = f"""### Application Design Overview
- **Application Type:** {app_type.title()}
- **Visual Style:** {visual_style.title()}
- **Brand Colors:** {', '.join(brand_colors) if brand_colors else 'Not detected'}
- **UI Patterns:** {', '.join(ui_patterns) if ui_patterns else 'Not detected'}

### Design Quality Assessment
{visual_summary[:500] + '...' if len(visual_summary) > 500 else visual_summary}

### Key Design Insights
"""

        if design_insights:
            for insight in design_insights:
                content += f"- {insight.strip()}\n"
        else:
            content += "- No specific design insights were identified\n"

        content += """
*Analysis performed using GPT-4 Vision on screenshots captured during the user flow.*"""

        return content


    def _format_content_analysis(self, chapters: Optional[List[Dict]], videos: Optional[List[Dict]], flow_summary: Dict) -> str:
        """
        Format chapter and video content analysis for inclusion in the markdown report.

        Args:
            chapters: Optional chapter content from CHAPTER steps
            videos: Optional video content from VIDEO steps
            flow_summary: Flow summary with enhanced content metrics

        Returns:
            Formatted markdown content for content analysis section
        """
        if not chapters and not videos:
            return ""

        content = f"""
---

## Content Structure Analysis

### Flow Organization
- **Total Chapters:** {len(chapters) if chapters else 0}
- **Total Video Segments:** {len(videos) if videos else 0}
- **Total Video Duration:** {flow_summary.get('total_video_duration', 0):.1f} seconds
"""

        # Add flow structure insights
        flow_structure = flow_summary.get('flow_structure', {})
        if flow_structure:
            content += f"""
### Flow Structure
- **Has Introduction:** {'Yes' if flow_structure.get('has_introduction') else 'No'}
- **Has Conclusion:** {'Yes' if flow_structure.get('has_conclusion') else 'No'}
- **Chapter Themes:** {', '.join(flow_structure.get('chapter_themes', [])) if flow_structure.get('chapter_themes') else 'None specified'}
"""

        # Add chapter details if available
        if chapters:
            content += """
### Chapter Breakdown
"""
            for i, chapter in enumerate(chapters, 1):
                title = chapter.get('title', f'Chapter {i}')
                subtitle = chapter.get('subtitle', '')
                button_text = chapter.get('button_text', '')

                content += f"**{i}. {title}**\n"
                if subtitle:
                    content += f"   - *{subtitle}*\n"
                if button_text:
                    content += f"   - Action: {button_text}\n"
                content += "\n"

        # Add video segment details if available
        if videos:
            content += """
### Video Segment Breakdown
"""
            for i, video in enumerate(videos, 1):
                duration = video.get('computed_duration', 0)
                segment_desc = video.get('segment_description', 'Unknown')
                playback_rate = video.get('playback_rate', 1)

                content += f"**Segment {i}: {segment_desc}**\n"
                content += f"   - Duration: {duration:.1f} seconds\n"
                if playback_rate != 1:
                    content += f"   - Playback Rate: {playback_rate}x\n"
                content += "\n"

        content += """*Analysis of chapter organization and video content structure from the flow data.*
"""

        return content

