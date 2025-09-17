"""
Flow Parser Module

This module contains the FlowParser class responsible for parsing and extracting
meaningful information from Arcade flow data.
"""

from typing import Dict, List, Any
import re
from urllib.parse import urlparse
from collections import Counter


class FlowParser:
    """Parses and extracts meaningful information from Arcade flow data."""

    def __init__(self, flow_data: Dict[str, Any]):
        """
        Initialize the FlowParser with flow data.

        Args:
            flow_data: The raw flow data dictionary from the JSON file
        """
        self.flow_data = flow_data
        self.steps = flow_data.get("steps", [])
        self.captured_events = flow_data.get("capturedEvents", [])
        self.flow_name = flow_data.get("name", "Unknown Flow")

    def extract_user_interactions(self) -> List[Dict[str, Any]]:
        """
        Extract and format user interactions from the flow data.

        Returns:
            List of interaction dictionaries with structured data
        """
        interactions = []

        # Process IMAGE steps with hotspots (user interactions)
        for step in self.steps:
            if step.get("type") == "IMAGE" and step.get("hotspots"):
                hotspot = step["hotspots"][0]  # Get the first hotspot
                page_context = step.get("pageContext", {})
                click_context = step.get("clickContext", {})

                interaction = {
                    "step_id": step["id"],
                    "action_type": "click",
                    "description": hotspot.get("label", "User interaction"),
                    "url": page_context.get("url", ""),
                    "page_title": page_context.get("title", ""),
                    "element_type": click_context.get("elementType", "unknown"),
                    "element_text": click_context.get("text", ""),
                    "css_selector": click_context.get("cssSelector", ""),
                    "coordinates": {"x": hotspot.get("x", 0), "y": hotspot.get("y", 0)},
                    "screenshot_url": step.get("url", ""),
                    "original_screenshot_url": step.get("originalImageUrl", ""),
                }
                interactions.append(interaction)

        return interactions

    def get_flow_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the flow metadata.

        Returns:
            Dictionary containing flow summary information
        """
        return {
            "name": self.flow_name,
            "description": self.flow_data.get("description", ""),
            "use_case": self.flow_data.get("useCase", ""),
            "total_steps": len(self.steps),
            "has_ai_processing": self.flow_data.get("hasUsedAI", False),
            "created": self.flow_data.get("created", {}),
            "schema_version": self.flow_data.get("schemaVersion", ""),
        }

    def analyze_user_journey(self) -> Dict[str, Any]:
        """
        Analyze the complete user journey through the flow.

        Returns:
            Dictionary containing journey analysis data
        """
        interactions = self.extract_user_interactions()

        # Extract key journey points
        journey_analysis = {
            "start_url": "",
            "end_url": "",
            "page_transitions": [],
            "key_actions": [],
            "total_interactions": len(interactions),
        }

        if interactions:
            journey_analysis["start_url"] = interactions[0]["url"]
            journey_analysis["end_url"] = interactions[-1]["url"]

            # Track page transitions
            current_url = ""
            for interaction in interactions:
                if interaction["url"] != current_url:
                    journey_analysis["page_transitions"].append(
                        {
                            "from": current_url,
                            "to": interaction["url"],
                            "page_title": interaction["page_title"],
                        }
                    )
                    current_url = interaction["url"]

            # Identify key actions
            for interaction in interactions:
                if any(
                    keyword in interaction["description"].lower()
                    for keyword in ["search", "click", "add to cart", "checkout"]
                ):
                    journey_analysis["key_actions"].append(
                        {
                            "action": interaction["description"],
                            "url": interaction["url"],
                            "element": interaction["element_text"],
                        }
                    )

        return journey_analysis

    def extract_screenshots(self) -> List[Dict[str, Any]]:
        """
        Extract all screenshots from the flow for visual analysis.

        Returns:
            List of screenshot dictionaries with metadata
        """
        screenshots = []

        for step in self.steps:
            if step.get("type") == "IMAGE" and step.get("url"):
                page_context = step.get("pageContext", {})

                screenshot = {
                    "step_id": step["id"],
                    "screenshot_url": step.get("url", ""),
                    "original_screenshot_url": step.get("originalImageUrl", ""),
                    "page_url": page_context.get("url", ""),
                    "page_title": page_context.get("title", ""),
                    "has_hotspots": bool(step.get("hotspots")),
                    "hotspot_coords": [
                        {"x": hs.get("x", 0), "y": hs.get("y", 0)}
                        for hs in step.get("hotspots", [])
                    ] if step.get("hotspots") else [],
                }
                screenshots.append(screenshot)

        return screenshots

    def extract_company_info(self) -> Dict[str, Any]:
        """
        Extract company and brand information from URLs and page titles.

        Returns:
            Dictionary containing company information for branding purposes
        """
        company_info = {
            "name": None,
            "domain": None,
            "brand_colors": {},
            "tagline": None,
            "detected_from": []
        }

        # Collect all URLs and page titles
        urls = []
        page_titles = []

        # Extract from flow name
        flow_name = self.flow_name.lower()

        # Extract from interactions
        interactions = self.extract_user_interactions()
        for interaction in interactions:
            if interaction["url"]:
                urls.append(interaction["url"])
            if interaction["page_title"]:
                page_titles.append(interaction["page_title"])

        # Extract from screenshots
        screenshots = self.extract_screenshots()
        for screenshot in screenshots:
            if screenshot["page_url"]:
                urls.append(screenshot["page_url"])
            if screenshot["page_title"]:
                page_titles.append(screenshot["page_title"])

        # Remove duplicates
        urls = list(set(urls))
        page_titles = list(set(page_titles))

        # Known company patterns
        company_patterns = {
            "target": {
                "name": "Target",
                "brand_colors": {"primary": "#CC0000", "secondary": "#FFFFFF"},
                "tagline": "Expect More. Pay Less.",
                "keywords": ["target", "target.com"]
            },
            "amazon": {
                "name": "Amazon",
                "brand_colors": {"primary": "#FF9900", "secondary": "#232F3E"},
                "tagline": "Earth's Most Customer-Centric Company",
                "keywords": ["amazon", "amazon.com"]
            },
            "walmart": {
                "name": "Walmart",
                "brand_colors": {"primary": "#0071CE", "secondary": "#FFFFFF"},
                "tagline": "Save Money. Live Better.",
                "keywords": ["walmart", "walmart.com"]
            }
        }

        # Analyze URLs for company detection
        for url in urls:
            parsed_url = urlparse(url.lower())
            domain = parsed_url.netloc.replace("www.", "")

            for company_key, company_data in company_patterns.items():
                if any(keyword in domain for keyword in company_data["keywords"]):
                    company_info["name"] = company_data["name"]
                    company_info["domain"] = domain
                    company_info["brand_colors"] = company_data["brand_colors"]
                    company_info["tagline"] = company_data["tagline"]
                    company_info["detected_from"].append(f"URL: {url}")
                    break

        # Analyze page titles for company detection
        for title in page_titles:
            title_lower = title.lower()
            for company_key, company_data in company_patterns.items():
                if any(keyword in title_lower for keyword in company_data["keywords"]):
                    if not company_info["name"]:  # Only set if not already detected
                        company_info["name"] = company_data["name"]
                        company_info["brand_colors"] = company_data["brand_colors"]
                        company_info["tagline"] = company_data["tagline"]
                    company_info["detected_from"].append(f"Title: {title}")
                    break

        # Analyze flow name for company detection
        for company_key, company_data in company_patterns.items():
            if any(keyword in flow_name for keyword in company_data["keywords"]):
                if not company_info["name"]:
                    company_info["name"] = company_data["name"]
                    company_info["brand_colors"] = company_data["brand_colors"]
                    company_info["tagline"] = company_data["tagline"]
                company_info["detected_from"].append(f"Flow name: {self.flow_name}")
                break

        # Fallback: Extract domain from first URL if no company detected
        if not company_info["name"] and urls:
            parsed_url = urlparse(urls[0].lower())
            domain = parsed_url.netloc.replace("www.", "")
            company_info["domain"] = domain
            # Try to extract company name from domain
            domain_parts = domain.split(".")
            if domain_parts:
                company_info["name"] = domain_parts[0].title()
                company_info["detected_from"].append(f"Domain extraction: {domain}")

        return company_info

    def extract_flow_context(self) -> Dict[str, Any]:
        """
        Dynamically extract context from any flow type.
        Works for shopping, booking, forms, searching, etc.

        Returns:
            Dictionary containing discovered flow context for dynamic image generation
        """
        flow_context = {
            "primary_action": None,
            "primary_object": None,
            "action_verbs": [],
            "key_nouns": [],
            "flow_type": "general",
            "completion_indicator": None,
            "context_confidence": 0.0
        }

        # Extract context from multiple sources
        flow_context.update(self._detect_primary_action())
        flow_context.update(self._detect_primary_object())
        flow_context.update(self._extract_action_verbs())
        flow_context.update(self._extract_key_nouns())
        flow_context.update(self._classify_flow_type())
        flow_context.update(self._find_completion_indicator())

        # Calculate confidence score
        flow_context["context_confidence"] = self._calculate_context_confidence(flow_context)

        return flow_context

    def extract_chapter_content(self) -> List[Dict[str, Any]]:
        """
        Extract content from CHAPTER steps for narrative context.

        Returns:
            List of chapter content dictionaries
        """
        chapters = []

        for step in self.steps:
            if step.get("type") == "CHAPTER":
                chapter_data = {
                    "id": step.get("id"),
                    "title": step.get("title", ""),
                    "subtitle": step.get("subtitle", ""),
                    "theme": step.get("theme", ""),
                    "text_align": step.get("textAlign", ""),
                    "show_preview_image": step.get("showPreviewImage", False),
                    "show_logo": step.get("showLogo", False),
                    "paths": step.get("paths", [])
                }

                # Extract button information for chapter navigation
                if chapter_data["paths"]:
                    for path in chapter_data["paths"]:
                        chapter_data["button_text"] = path.get("buttonText", "")
                        chapter_data["path_type"] = path.get("pathType", "")
                        if path.get("url"):
                            chapter_data["target_url"] = path.get("url")

                chapters.append(chapter_data)

        return chapters

    def extract_video_content(self) -> List[Dict[str, Any]]:
        """
        Extract content from VIDEO steps for interaction timing analysis.

        Returns:
            List of video content dictionaries
        """
        videos = []

        for step in self.steps:
            if step.get("type") == "VIDEO":
                video_data = {
                    "id": step.get("id"),
                    "url": step.get("url"),
                    "start_time_frac": step.get("startTimeFrac", 0),
                    "end_time_frac": step.get("endTimeFrac", 1),
                    "playback_rate": step.get("playbackRate", 1),
                    "duration": step.get("duration", 0),
                    "muted": step.get("muted", True),
                    "thumbnail_url": step.get("videoThumbnailUrl"),
                    "size": step.get("size", {}),
                    "computed_duration": 0,
                    "segment_description": ""
                }

                # Calculate segment duration
                total_duration = video_data["duration"]
                start_frac = video_data["start_time_frac"]
                end_frac = video_data["end_time_frac"]

                video_data["computed_duration"] = total_duration * (end_frac - start_frac)
                video_data["start_time_seconds"] = total_duration * start_frac
                video_data["end_time_seconds"] = total_duration * end_frac

                # Generate a description based on timing
                if start_frac < 0.1:
                    video_data["segment_description"] = "Introduction/Setup"
                elif start_frac < 0.3:
                    video_data["segment_description"] = "Early Interaction"
                elif start_frac < 0.7:
                    video_data["segment_description"] = "Main Interaction"
                else:
                    video_data["segment_description"] = "Completion/Final Steps"

                videos.append(video_data)

        return videos

    def get_enhanced_flow_summary(self) -> Dict[str, Any]:
        """
        Generate an enhanced summary including chapter and video content.

        Returns:
            Dictionary containing comprehensive flow summary
        """
        base_summary = self.get_flow_summary()
        chapters = self.extract_chapter_content()
        videos = self.extract_video_content()

        # Add enhanced content analysis
        base_summary.update({
            "total_chapters": len(chapters),
            "total_video_segments": len(videos),
            "total_video_duration": sum(v["computed_duration"] for v in videos),
            "flow_structure": {
                "has_introduction": len(chapters) > 0 and ("intro" in chapters[0]["title"].lower() if chapters[0]["title"] else False),
                "has_conclusion": any(c["title"] for c in chapters if c["title"] and ("thank" in c["title"].lower() or "complete" in c["title"].lower())),
                "chapter_themes": list(set(c["theme"] for c in chapters if c["theme"])),
                "video_segments": [v["segment_description"] for v in videos]
            }
        })

        return base_summary

    def _detect_primary_action(self) -> Dict[str, Any]:
        """Extract main action from flow name and interactions"""
        flow_name = self.flow_name.lower()

        # Common action patterns (ordered by specificity)
        action_patterns = [
            (r"add (.+?) to (.+)", "Add to"),
            (r"book (.+?) on", "Book"),
            (r"reserve (.+?) on", "Reserve"),
            (r"search for (.+)", "Search for"),
            (r"find (.+?) on", "Find"),
            (r"create (.+?) on", "Create"),
            (r"submit (.+?) to", "Submit"),
            (r"checkout (.+)", "Checkout"),
            (r"complete (.+)", "Complete"),
            (r"browse (.+)", "Browse"),
            (r"view (.+)", "View"),
            (r"select (.+)", "Select"),
            (r"choose (.+)", "Choose"),
        ]

        # Check flow name first
        for pattern, action in action_patterns:
            match = re.search(pattern, flow_name)
            if match:
                return {"primary_action": action.strip()}

        # Fall back to analyzing interactions for action verbs
        interactions = self.extract_user_interactions()
        action_verbs = []

        for interaction in interactions:
            description = interaction.get("description", "").lower()
            # Extract common action verbs
            verbs = re.findall(r'\b(click|tap|select|choose|add|search|book|submit|create|view|browse|checkout|complete|visit|decline)\b', description)
            action_verbs.extend(verbs)

        if action_verbs:
            # Find most common action verb
            most_common_verb = Counter(action_verbs).most_common(1)[0][0]
            return {"primary_action": most_common_verb.title()}

        return {"primary_action": "Complete Task"}

    def _detect_primary_object(self) -> Dict[str, Any]:
        """Extract main object from flow name and interactions"""
        flow_name = self.flow_name.lower()

        # Object extraction patterns
        object_patterns = [
            (r"add (?:a |an |the )?(.+?) to (?:your )?cart", r"\1"),
            (r"book (?:a |an |the )?(.+?) on", r"\1"),
            (r"search for (?:a |an |the )?(.+)", r"\1"),
            (r"find (?:a |an |the )?(.+?) on", r"\1"),
            (r"create (?:a |an |the )?(.+?) on", r"\1"),
            (r"submit (?:a |an |the )?(.+?) to", r"\1"),
            (r"(?:buy|purchase) (?:a |an |the )?(.+)", r"\1"),
        ]

        # Check flow name patterns
        for pattern, replacement in object_patterns:
            match = re.search(pattern, flow_name)
            if match:
                object_text = match.group(1).strip()
                # Clean up the object text
                object_text = re.sub(r'\s+on\s+\w+\.com$', '', object_text)  # Remove "on domain.com"
                object_text = re.sub(r'\s+to\s+your\s+cart$', '', object_text)  # Remove "to your cart"
                return {"primary_object": object_text.title()}

        # Fall back to analyzing interactions for object mentions
        interactions = self.extract_user_interactions()
        object_mentions = []

        for interaction in interactions:
            description = interaction.get("description", "").lower()
            element_text = interaction.get("element_text", "").lower()

            # Look for product/object mentions in descriptions
            # Extract nouns that might be products
            words = re.findall(r'\b[a-z]{3,}\b', description + " " + element_text)
            # Filter out common UI words
            ui_words = {"click", "tap", "select", "button", "cart", "checkout", "search", "bar", "image", "page", "website", "site"}
            object_words = [word for word in words if word not in ui_words and len(word) > 3]
            object_mentions.extend(object_words)

        if object_mentions:
            # Find most mentioned object
            most_common_object = Counter(object_mentions).most_common(1)[0][0]
            return {"primary_object": most_common_object.title()}

        return {"primary_object": None}

    def _extract_action_verbs(self) -> Dict[str, Any]:
        """Extract all action verbs from interactions"""
        interactions = self.extract_user_interactions()
        action_verbs = []

        for interaction in interactions:
            description = interaction.get("description", "").lower()
            # Extract action verbs
            verbs = re.findall(r'\b(click|tap|select|choose|add|search|book|submit|create|view|browse|checkout|complete|visit|decline|explore|personalize|secure)\b', description)
            action_verbs.extend(verbs)

        return {"action_verbs": list(set(action_verbs))}

    def _extract_key_nouns(self) -> Dict[str, Any]:
        """Extract key nouns that might represent objects or concepts"""
        flow_name = self.flow_name.lower()
        interactions = self.extract_user_interactions()

        all_text = flow_name + " "
        for interaction in interactions:
            all_text += interaction.get("description", "") + " "
            all_text += interaction.get("element_text", "") + " "

        # Extract potential nouns (3+ letters, not common UI words)
        words = re.findall(r'\b[a-z]{3,}\b', all_text.lower())
        ui_words = {"click", "tap", "select", "button", "cart", "checkout", "search", "bar", "image", "page", "website", "site", "your", "the", "and", "for", "with", "from", "this", "that"}
        key_nouns = [word for word in words if word not in ui_words]

        # Count and return most frequent nouns
        noun_counts = Counter(key_nouns)
        return {"key_nouns": [noun for noun, count in noun_counts.most_common(5)]}

    def _classify_flow_type(self) -> Dict[str, Any]:
        """Classify the type of flow based on actions and context"""
        flow_name = self.flow_name.lower()
        interactions = self.extract_user_interactions()

        # Collect all text for analysis
        all_text = flow_name + " "
        for interaction in interactions:
            all_text += interaction.get("description", "") + " "

        all_text = all_text.lower()

        # Flow type indicators
        flow_indicators = {
            "e-commerce": ["cart", "checkout", "buy", "purchase", "add to cart", "product", "price", "shopping"],
            "booking": ["book", "reserve", "reservation", "schedule", "appointment", "flight", "hotel", "ticket"],
            "search": ["search", "find", "look for", "browse", "filter", "results"],
            "form": ["submit", "form", "fill", "complete", "application", "register", "sign up"],
            "social": ["post", "share", "like", "comment", "follow", "message", "profile"],
            "content": ["read", "view", "watch", "article", "video", "news", "blog"],
            "navigation": ["menu", "navigate", "browse", "explore", "category"]
        }

        # Score each flow type
        type_scores = {}
        for flow_type, keywords in flow_indicators.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                type_scores[flow_type] = score

        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            return {"flow_type": best_type}

        return {"flow_type": "general"}

    def _find_completion_indicator(self) -> Dict[str, Any]:
        """Find what indicates completion of the flow"""
        interactions = self.extract_user_interactions()

        if not interactions:
            return {"completion_indicator": None}

        # Look at the last few interactions for completion indicators
        last_interaction = interactions[-1]
        last_description = last_interaction.get("description", "").lower()

        completion_patterns = [
            ("cart", "cart"),
            ("checkout", "checkout"),
            ("confirmation", "confirmation"),
            ("success", "success"),
            ("complete", "completion"),
            ("submit", "submission"),
            ("finish", "finish"),
            ("done", "done")
        ]

        for pattern, indicator in completion_patterns:
            if pattern in last_description:
                return {"completion_indicator": indicator}

        # Fall back to URL analysis
        last_url = last_interaction.get("url", "").lower()
        for pattern, indicator in completion_patterns:
            if pattern in last_url:
                return {"completion_indicator": indicator}

        return {"completion_indicator": "completion"}

    def _calculate_context_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence score for the extracted context"""
        confidence = 0.0

        # Add confidence based on what we detected
        if context.get("primary_action"):
            confidence += 0.3
        if context.get("primary_object"):
            confidence += 0.3
        if context.get("action_verbs"):
            confidence += 0.2
        if context.get("flow_type") != "general":
            confidence += 0.2

        return min(confidence, 1.0)
