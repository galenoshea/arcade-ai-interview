"""
AI Analysis Module

This module contains the AIAnalyzer class responsible for AI-powered analysis
using OpenAI's GPT-4 and DALL-E 3 for user intent analysis and image generation.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import openai
import requests

from .cache import CacheManager
from .config import get_config

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Handles AI-powered analysis using OpenAI's GPT-4 and DALL-E."""

    # JSON Schema for structured outputs (2025 OpenAI feature)
    ANALYSIS_SCHEMA = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "A 2-3 sentence summary of what the user accomplished"
            },
            "user_goal": {
                "type": "string",
                "description": "What the user was trying to achieve (be specific)"
            },
            "key_insights": {
                "type": "string",
                "description": "3-4 bullet points about the user's behavior and flow effectiveness"
            }
        },
        "required": ["summary", "user_goal", "key_insights"],
        "additionalProperties": False
    }

    # Tiered model configuration for cost optimization
    MODEL_TIERS = {
        "premium": {
            "model": "gpt-4o",
            "use_case": "Complex analysis requiring deep insights",
            "cost_per_1k": 0.03,  # Approximate pricing
            "max_tokens": 4000
        },
        "standard": {
            "model": "gpt-3.5-turbo",
            "use_case": "Standard analysis and processing",
            "cost_per_1k": 0.002,  # Approximate pricing
            "max_tokens": 4000
        },
        "vision": {
            "model": "gpt-4o",
            "use_case": "Visual analysis of screenshots",
            "cost_per_1k": 0.01,  # Approximate pricing for vision
            "max_tokens": 4000
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AIAnalyzer.

        Args:
            api_key: Optional OpenAI API key. Uses config default if not provided.
        """
        config = get_config()
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = openai.OpenAI(api_key=self.api_key)
        self.cache = CacheManager()
        self.config = config
        self.cost_tracker = {"total_cost": 0.0, "model_usage": {}}

    def _select_model_tier(self,
                          task_type: str,
                          complexity_indicators: Dict = None) -> str:
        """
        Select the appropriate model tier based on task complexity and requirements.

        Args:
            task_type: Type of task (analysis, vision, generation)
            complexity_indicators: Dictionary with complexity metrics

        Returns:
            Model tier key ('premium', 'standard', 'vision')
        """
        if complexity_indicators is None:
            complexity_indicators = {}

        # Vision tasks always use vision model
        if task_type == "vision":
            return "vision"

        # For analysis tasks, determine complexity
        if task_type == "analysis":
            interactions_count = complexity_indicators.get("interactions_count", 0)
            has_visual_context = complexity_indicators.get("has_visual_context", False)
            flow_steps = complexity_indicators.get("flow_steps", 0)

            # Use premium model for complex flows
            if (interactions_count > 5 or
                has_visual_context or
                flow_steps > 10):
                logger.info("Using premium model for complex analysis")
                return "premium"
            else:
                logger.info("Using standard model for simple analysis")
                return "standard"

        # Default to standard for unknown tasks
        return "standard"

    def _track_api_cost(self, model_tier: str, tokens_used: int) -> None:
        """
        Track API costs for cost optimization analysis.

        Args:
            model_tier: The model tier used ('premium', 'standard', 'vision')
            tokens_used: Number of tokens consumed
        """
        cost_per_1k = self.MODEL_TIERS[model_tier]["cost_per_1k"]
        call_cost = (tokens_used / 1000) * cost_per_1k

        self.cost_tracker["total_cost"] += call_cost

        if model_tier not in self.cost_tracker["model_usage"]:
            self.cost_tracker["model_usage"][model_tier] = {
                "calls": 0,
                "tokens": 0,
                "cost": 0.0
            }

        self.cost_tracker["model_usage"][model_tier]["calls"] += 1
        self.cost_tracker["model_usage"][model_tier]["tokens"] += tokens_used
        self.cost_tracker["model_usage"][model_tier]["cost"] += call_cost

        logger.info(f"API call cost: ${call_cost:.4f} ({model_tier} model, {tokens_used} tokens)")

    def get_cost_summary(self) -> Dict:
        """
        Get a summary of API costs and usage statistics.

        Returns:
            Dictionary containing cost breakdown and optimization insights
        """
        savings_estimate = 0.0
        if "standard" in self.cost_tracker["model_usage"]:
            standard_usage = self.cost_tracker["model_usage"]["standard"]
            # Estimate savings from using standard instead of premium
            premium_cost_estimate = (standard_usage["tokens"] / 1000) * self.MODEL_TIERS["premium"]["cost_per_1k"]
            actual_cost = standard_usage["cost"]
            savings_estimate = premium_cost_estimate - actual_cost

        return {
            "total_cost": self.cost_tracker["total_cost"],
            "model_breakdown": self.cost_tracker["model_usage"],
            "estimated_savings": savings_estimate,
            "optimization_enabled": True
        }

    def analyze_user_intent(
        self, interactions: List[Dict], flow_summary: Dict, visual_analysis: Dict = None
    ) -> Dict[str, str]:
        """
        Use GPT-4 to analyze user intent and generate human-readable descriptions.
        Enhanced with visual context from screenshot analysis.

        Args:
            interactions: List of user interactions
            flow_summary: Flow metadata summary
            visual_analysis: Optional visual analysis results from GPT-4 Vision

        Returns:
            Dictionary containing analysis results
        """
        # Create cache key from interactions data and visual analysis
        cache_data = json.dumps(interactions) + json.dumps(flow_summary)
        if visual_analysis:
            cache_data += json.dumps(visual_analysis)
        cache_key = self.cache._get_cache_key(cache_data)

        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        # Determine model tier based on task complexity
        complexity_indicators = {
            "interactions_count": len(interactions),
            "has_visual_context": visual_analysis is not None,
            "flow_steps": flow_summary.get("total_steps", 0)
        }
        model_tier = self._select_model_tier("analysis", complexity_indicators)
        selected_model = self.MODEL_TIERS[model_tier]["model"]

        # Prepare the prompt for selected model
        prompt = self._create_analysis_prompt(interactions, flow_summary, visual_analysis)

        try:
            logger.info(f"Sending request to {selected_model} for user intent analysis...")
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert UX analyst specializing in e-commerce user behavior analysis. Provide professional, insightful analysis of user interactions in JSON format.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.3,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "user_flow_analysis",
                        "schema": self.ANALYSIS_SCHEMA
                    }
                }
            )

            # With structured outputs, we get guaranteed JSON compliance
            result = json.loads(response.choices[0].message.content)

            # Track API costs for optimization analysis
            tokens_used = response.usage.total_tokens if response.usage else 1000  # Fallback estimate
            self._track_api_cost(model_tier, tokens_used)

            # Cache the result
            self.cache.set(cache_key, result)

            logger.info(f"Successfully completed {selected_model} analysis with structured outputs")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze user intent: {e}")
            return {
                "summary": f"Analysis of {flow_summary.get('name', 'user flow')}",
                "user_goal": "Unable to determine user goal due to API error",
                "key_insights": "AI analysis temporarily unavailable",
            }

    def _create_analysis_prompt(
        self, interactions: List[Dict], flow_summary: Dict, visual_analysis: Dict = None
    ) -> str:
        """
        Create a detailed prompt for GPT-4 analysis with optional visual context.

        Args:
            interactions: List of user interactions
            flow_summary: Flow metadata summary
            visual_analysis: Optional visual analysis results from GPT-4 Vision

        Returns:
            Formatted prompt string
        """
        interactions_text = "\n".join(
            [
                f"- {i+1}. {interaction['description']} (on {interaction['page_title']})"
                for i, interaction in enumerate(interactions)
            ]
        )

        # Build visual context if available
        visual_context = ""
        if visual_analysis and visual_analysis.get("visual_summary"):
            visual_context = f"""

        Visual Context (from screenshot analysis):
        - Application Type: {visual_analysis.get('app_type', 'unknown')}
        - Visual Style: {visual_analysis.get('visual_style', 'unknown')}
        - Brand Colors: {', '.join(visual_analysis.get('brand_colors', []))}
        - UI Patterns: {', '.join(visual_analysis.get('ui_patterns', []))}
        - Design Quality: {visual_analysis.get('visual_summary', '')[:200]}...
        """

        return f"""
        Analyze this user flow from {flow_summary.get('name', 'an e-commerce website')}:

        Flow Overview:
        - Name: {flow_summary.get('name', 'Unknown')}
        - Total Steps: {flow_summary.get('total_steps', 0)}
        - Use Case: {flow_summary.get('use_case', 'Not specified')}

        User Interactions:
        {interactions_text}
        {visual_context}

        Provide your analysis in JSON format with the following fields:
        - summary: A 2-3 sentence summary of what the user accomplished
        - user_goal: What the user was trying to achieve (be specific)
        - key_insights: 3-4 bullet points about the user's behavior and the flow effectiveness, incorporating visual design insights when available
        """


    def analyze_screenshots(
        self, screenshots: List[Dict], interactions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze screenshots using GPT-4 Vision to understand visual context.

        Args:
            screenshots: List of screenshot metadata with URLs
            interactions: List of user interactions for context

        Returns:
            Dictionary containing visual analysis results
        """
        if not screenshots:
            return {
                "visual_summary": "No screenshots available for analysis",
                "ui_patterns": [],
                "design_insights": [],
                "app_type": "unknown",
                "brand_colors": [],
                "visual_style": "unknown",
            }

        # Create cache key for vision analysis
        cache_key = self.cache._get_cache_key(
            f"vision_{len(screenshots)}_{screenshots[0].get('screenshot_url', '')}"
        )

        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info("Vision analysis cache hit")
            return cached_result

        try:
            # Analyze the first few screenshots for comprehensive understanding
            analysis_screenshots = screenshots[:3]  # Analyze first 3 for efficiency

            logger.info(
                f"Analyzing {len(analysis_screenshots)} screenshots with GPT-4 Vision..."
            )

            # Create vision analysis prompt
            visual_analysis = self._analyze_screenshot_batch(
                analysis_screenshots, interactions
            )

            # Cache the result
            self.cache.set(cache_key, visual_analysis)
            return visual_analysis

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            return {
                "visual_summary": f"Vision analysis failed: {str(e)}",
                "ui_patterns": [],
                "design_insights": [],
                "app_type": "unknown",
                "brand_colors": [],
                "visual_style": "unknown",
            }

    def _analyze_screenshot_batch(
        self, screenshots: List[Dict], interactions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze a batch of screenshots with GPT-4 Vision.

        Args:
            screenshots: List of screenshots to analyze
            interactions: User interactions for context

        Returns:
            Visual analysis results
        """
        # Prepare messages for vision analysis
        messages = [
            {
                "role": "system",
                "content": """You are an expert UI/UX analyst specializing in visual design analysis.
                Analyze the provided screenshots to understand:
                1. Application type and industry
                2. Visual design patterns and UI elements
                3. Brand colors and visual style
                4. User experience quality and design insights

                Provide professional analysis suitable for UX reports.""",
            }
        ]

        # Add screenshots to the analysis
        content = [
            {
                "type": "text",
                "text": f"""Analyze these {len(screenshots)} screenshots from a user flow.

                Context: User performed these actions: {', '.join([i.get('description', '') for i in interactions[:5]])}

                Please analyze:
                1. What type of application/website is this?
                2. What are the main UI patterns and design elements?
                3. What are the primary brand colors used?
                4. What's the overall visual style (modern, classic, minimal, etc.)?
                5. Any notable UX insights about the design quality?

                Provide specific observations about the visual design.""",
            }
        ]

        # Add each screenshot URL
        for screenshot in screenshots:
            if screenshot.get("screenshot_url"):
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": screenshot["screenshot_url"],
                            "detail": "low",  # Use low detail for cost efficiency
                        },
                    }
                )

        messages.append({"role": "user", "content": content})

        # Call GPT-4o for vision analysis
        response = self.client.chat.completions.create(
            model="gpt-4o", messages=messages, max_tokens=800
        )

        analysis_text = response.choices[0].message.content

        # Track API costs for vision analysis
        tokens_used = response.usage.total_tokens if response.usage else 800  # Fallback estimate
        self._track_api_cost("vision", tokens_used)

        # Parse the response into structured data
        return self._parse_vision_response(analysis_text)

    def _parse_vision_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse GPT-4 Vision response into structured visual analysis.

        Args:
            response_text: Raw response from GPT-4 Vision

        Returns:
            Structured visual analysis dictionary
        """
        # Extract key information from the response
        # This is a simple parser - could be enhanced with structured outputs
        lines = response_text.lower()

        # Determine application type
        app_type = "web application"
        if "e-commerce" in lines or "shopping" in lines or "cart" in lines:
            app_type = "e-commerce"
        elif "social" in lines or "media" in lines:
            app_type = "social media"
        elif "dashboard" in lines or "analytics" in lines:
            app_type = "dashboard"
        elif "mobile" in lines or "app" in lines:
            app_type = "mobile application"

        # Extract visual style
        visual_style = "modern"
        if "minimal" in lines:
            visual_style = "minimal"
        elif "classic" in lines or "traditional" in lines:
            visual_style = "classic"
        elif "bold" in lines or "vibrant" in lines:
            visual_style = "bold"

        # Extract colors mentioned
        color_keywords = ["blue", "red", "green", "orange", "purple", "white", "black"]
        brand_colors = [color for color in color_keywords if color in lines]

        return {
            "visual_summary": response_text,
            "ui_patterns": self._extract_ui_patterns(response_text),
            "design_insights": self._extract_design_insights(response_text),
            "app_type": app_type,
            "brand_colors": brand_colors,
            "visual_style": visual_style,
        }

    def _extract_ui_patterns(self, text: str) -> List[str]:
        """Extract UI patterns mentioned in the analysis."""
        patterns = []
        ui_keywords = [
            "navigation",
            "search bar",
            "buttons",
            "forms",
            "cards",
            "grid",
            "sidebar",
            "header",
            "footer",
            "menu",
        ]

        for keyword in ui_keywords:
            if keyword in text.lower():
                patterns.append(keyword)

        return patterns

    def _extract_design_insights(self, text: str) -> List[str]:
        """Extract design insights from the analysis."""
        insights = []

        # Split into sentences and find insightful ones
        sentences = text.split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            if (
                len(sentence) > 20
                and any(
                    word in sentence.lower()
                    for word in ["design", "user", "interface", "experience", "visual"]
                )
            ):
                insights.append(sentence)

        return insights[:3]  # Return top 3 insights

    def generate_social_media_image(
        self, flow_summary: Dict, analysis: Dict, visual_analysis: Dict = None, company_info: Dict = None, flow_context: Dict = None
    ) -> Optional[str]:
        """
        Generate a social media image using DALL-E 3.
        Enhanced with dynamic flow context discovery and company branding.

        Args:
            flow_summary: Flow metadata summary
            analysis: Analysis results
            visual_analysis: Optional visual analysis results from GPT-4 Vision
            company_info: Optional company branding information for customized prompts
            flow_context: Optional discovered flow context (action, object, type)

        Returns:
            Path to generated image file, or None if failed
        """
        # Create cache key including visual analysis
        cache_data = f"dalle_{flow_summary.get('name', '')}"
        if visual_analysis:
            cache_data += f"_{visual_analysis.get('app_type', '')}_{visual_analysis.get('visual_style', '')}"
        cache_key = self.cache._get_cache_key(cache_data)

        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result and cached_result.get("image_path"):
            image_path = cached_result["image_path"]
            if Path(image_path).exists():
                return image_path

        # Create a compelling prompt for the social media image
        prompt = self._create_image_prompt(flow_summary, analysis, visual_analysis, company_info, flow_context)

        try:
            logger.info("Generating social media image with DALL-E 3...")
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            # Download and save the image
            image_url = response.data[0].url
            image_path = self._download_and_save_image(
                image_url, "social_media_image.png"
            )

            # Cache the result
            self.cache.set(cache_key, {"image_path": image_path})

            logger.info(f"Successfully generated social media image: {image_path}")
            return image_path

        except Exception as e:
            logger.error(f"Failed to generate social media image: {e}")
            return None

    def _create_image_prompt(self, flow_summary: Dict, analysis: Dict, visual_analysis: Dict = None, company_info: Dict = None, flow_context: Dict = None) -> str:
        """
        Create an adaptive prompt for DALL-E 3 based on discovered flow context and company branding.

        Args:
            flow_summary: Flow metadata summary
            analysis: Analysis results
            visual_analysis: Optional visual analysis results from GPT-4 Vision
            company_info: Optional company branding information for customized prompts
            flow_context: Optional discovered flow context (action, object, type)

        Returns:
            Formatted image generation prompt optimized for text legibility and actual flow representation
        """
        # DYNAMIC FLOW CONTEXT APPROACH
        # Generate prompts based on discovered flow context, not hardcoded assumptions

        # Extract discovered context
        action = flow_context.get("primary_action", "Complete Task") if flow_context else "Complete Task"
        object_name = flow_context.get("primary_object", "") if flow_context else ""
        flow_type = flow_context.get("flow_type", "general") if flow_context else "general"
        completion = flow_context.get("completion_indicator", "completion") if flow_context else "completion"
        confidence = flow_context.get("context_confidence", 0.0) if flow_context else 0.0

        # Build dynamic text based on discovered context
        if object_name and action:
            # We have both action and object: "Add Scooter", "Book Flight", "Search Products"
            if action == "Add to":
                primary_text = f"Add {object_name}"
            else:
                primary_text = f"{action} {object_name}"
        elif action:
            # We have action but no object: "Search", "Complete", "Submit"
            primary_text = action
        else:
            # Fallback to generic
            primary_text = "Complete Task"

        # Build secondary text based on platform or completion
        company_name = company_info.get("name", "") if company_info else ""
        if company_name:
            secondary_text = f"on {company_name}"
        else:
            secondary_text = "Made Easy"

        # Determine colors based on company or flow type
        if company_info and company_info.get("brand_colors"):
            brand_colors = company_info["brand_colors"]
            primary_color = brand_colors.get("primary", "#0066CC")
            secondary_color = brand_colors.get("secondary", "#FFFFFF")
            color_scheme = f"{primary_color} and {secondary_color}"
            if company_name:
                style_description = f"{company_name}'s brand aesthetic"
            else:
                style_description = "professional brand design"
        else:
            # Default colors based on flow type
            if flow_type == "e-commerce":
                color_scheme = "blue (#0066CC) and white (#FFFFFF)"
                style_description = "modern e-commerce design"
            elif flow_type == "booking":
                color_scheme = "green (#00AA44) and white (#FFFFFF)"
                style_description = "professional booking interface"
            elif flow_type == "search":
                color_scheme = "orange (#FF6600) and white (#FFFFFF)"
                style_description = "dynamic search interface"
            else:
                color_scheme = "blue (#0066CC) and white (#FFFFFF)"
                style_description = "clean modern design"

        # Determine visual elements based on flow type and object
        visual_elements = []

        if flow_type == "e-commerce":
            visual_elements = ["shopping cart", "product display", "add to cart button"]
            if object_name:
                visual_elements.insert(0, object_name.lower())
        elif flow_type == "booking":
            visual_elements = ["calendar", "booking confirmation", "schedule interface"]
            if object_name:
                visual_elements.insert(0, object_name.lower())
        elif flow_type == "search":
            visual_elements = ["search bar", "results grid", "filter options"]
            if object_name:
                visual_elements.append(f"{object_name.lower()} results")
        elif flow_type == "form":
            visual_elements = ["form fields", "submit button", "completion checkmark"]
        else:
            # General/unknown flow type
            visual_elements = ["modern interface", "action buttons", "completion indicator"]
            if object_name:
                visual_elements.insert(0, object_name.lower())

        # Add company-specific elements if available
        if company_name:
            visual_elements.append(f"{company_name} branding")

        visual_elements_text = ", ".join(visual_elements)

        # Build the final prompt
        return f"""
        Create a professional social media image that represents the user action: "{primary_text} {secondary_text}".
        This image should clearly show what the user accomplished in their journey.

        CONTEXT REQUIREMENTS:
        - Flow Type: {flow_type}
        - Primary Action: {action}
        - Object/Focus: {object_name if object_name else 'general task'}
        - Confidence: {confidence:.1f}/1.0

        TEXT OVERLAY REQUIREMENTS (CRITICAL FOR LEGIBILITY):
        - Primary text: "{primary_text}" (large, bold, high contrast)
        - Secondary text: "{secondary_text}" (medium size, clear)
        - Font: Bold sans-serif (like Helvetica Bold or Arial Black)
        - Text placement: Top or bottom third with solid background
        - Text size: Minimum 48pt for primary, 32pt for secondary
        - High contrast: Use {color_scheme} for maximum readability
        - Text background: Solid color block for maximum legibility
        - NO text overlapping complex backgrounds

        VISUAL ELEMENTS:
        - Main elements: {visual_elements_text}
        - Style: {style_description}
        - Composition: Clean, uncluttered layout
        - Focus: Clearly represent the action "{primary_text}"
        - Include: Visual representation of what the user actually did

        COMPOSITION REQUIREMENTS:
        - 70% visual elements showing the action/object
        - 30% clear space for legible text
        - Professional appearance suitable for social media
        - Immediately understandable what action was completed
        - Optimized for engagement and clarity
        """

        # Keep visual_analysis fallback for when we don't have flow context
        if visual_analysis:
            # Enhanced visual analysis with legibility focus
            app_type = visual_analysis.get("app_type", "e-commerce")
            visual_style = visual_analysis.get("visual_style", "modern")
            brand_colors = visual_analysis.get("brand_colors", [])

            # Create simplified text overlay
            simple_text = "Easy Shopping"
            if "cart" in flow_name.lower():
                simple_text = "Add to Cart"
            elif "search" in flow_name.lower():
                simple_text = "Smart Search"
            elif "checkout" in flow_name.lower():
                simple_text = "Quick Checkout"

            color_scheme = "blue and white"
            if brand_colors:
                color_scheme = f"{brand_colors[0]} and white" if brand_colors else "blue and white"

            return f"""
            Create a professional social media image for {app_type} tutorial content.

            TEXT OVERLAY REQUIREMENTS (CRITICAL FOR LEGIBILITY):
            - Primary text: "{simple_text}" (large, bold, high contrast)
            - Font: Bold sans-serif (like Helvetica Bold)
            - Text size: Minimum 48pt
            - Text placement: Clear area with solid background
            - High contrast: White text on colored background OR dark text on white background
            - NO text overlapping complex backgrounds

            VISUAL STYLE:
            - {visual_style} {app_type} design
            - Color scheme: {color_scheme}
            - Include: shopping cart icons, mobile interface, clean product displays
            - Composition: 70% visual elements, 30% clear text area

            The image should be immediately readable and professional for social media sharing.
            """

        else:
            # Fallback with emphasis on text legibility
            return f"""
            Create a modern, professional social media image for e-commerce tutorial.

            TEXT OVERLAY REQUIREMENTS (CRITICAL FOR LEGIBILITY):
            - Primary text: "Easy Shopping" (large, bold, high contrast)
            - Font: Bold sans-serif (like Helvetica Bold)
            - Text size: Minimum 48pt
            - Text placement: Top or bottom with solid background
            - High contrast: White text on blue background
            - Clear, readable typography - NO decorative fonts

            VISUAL ELEMENTS:
            - Clean e-commerce design with shopping cart icons
            - Mobile and desktop interface mockups
            - Blue and white color scheme
            - Professional composition optimized for social media

            Prioritize text readability above all other design elements.
            """

    def _download_and_save_image(self, image_url: str, filename: str) -> Optional[str]:
        """
        Download and save the generated image.

        Args:
            image_url: URL of the generated image
            filename: Desired filename for the saved image

        Returns:
            Path to saved image file, or None if failed
        """
        try:
            response = requests.get(image_url)
            response.raise_for_status()

            # Use the results directory from config
            output_path = self.config.RESULTS_DIR / filename
            with open(output_path, "wb") as f:
                f.write(response.content)

            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return None
