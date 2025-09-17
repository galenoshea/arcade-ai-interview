"""
Behavioral Analytics Module

This module analyzes user behavior patterns from Arcade flow data to extract
meaningful insights about user decision-making, timing, and engagement.
"""

from typing import Dict, List, Any, Optional
import statistics
from datetime import datetime


class BehavioralAnalyzer:
    """Analyzes user behavior patterns and interaction timing."""

    def __init__(self, flow_data: Dict[str, Any]):
        """
        Initialize the behavioral analyzer with flow data.

        Args:
            flow_data: The raw flow data dictionary from the JSON file
        """
        self.flow_data = flow_data
        self.captured_events = flow_data.get("capturedEvents", [])
        self.steps = flow_data.get("steps", [])

    def analyze_user_behavior(self) -> Dict[str, Any]:
        """
        Perform comprehensive behavioral analysis.

        Returns:
            Dictionary containing behavioral analytics results
        """
        behavior_analysis = {
            "timing_analysis": self._analyze_timing_patterns(),
            "interaction_velocity": self._calculate_interaction_velocity(),
            "decision_patterns": self._analyze_decision_patterns(),
            "engagement_score": self._calculate_engagement_score(),
            "confidence_indicators": self._assess_user_confidence(),
            "journey_efficiency": self._measure_journey_efficiency(),
            "precision_analytics": self._analyze_interaction_precision(),
            "behavior_insights": self._generate_behavior_insights()
        }

        return behavior_analysis

    def _analyze_timing_patterns(self) -> Dict[str, Any]:
        """Analyze timing patterns between user interactions."""
        click_events = [e for e in self.captured_events if e.get("type") == "click"]

        if len(click_events) < 2:
            return {"error": "Insufficient click events for timing analysis"}

        times = [e["timeMs"] for e in click_events]
        times.sort()

        # Calculate delays between clicks
        delays = []
        for i in range(1, len(times)):
            delay = (times[i] - times[i-1]) / 1000  # Convert to seconds
            delays.append(delay)

        total_duration = (times[-1] - times[0]) / 1000

        return {
            "total_duration_seconds": round(total_duration, 1),
            "total_interactions": len(click_events),
            "interaction_delays": [round(d, 1) for d in delays],
            "average_delay": round(statistics.mean(delays), 1),
            "median_delay": round(statistics.median(delays), 1),
            "min_delay": round(min(delays), 1),
            "max_delay": round(max(delays), 1),
            "delay_variance": round(statistics.variance(delays) if len(delays) > 1 else 0, 1),
            "interaction_tempo": self._classify_interaction_tempo(delays)
        }

    def _calculate_interaction_velocity(self) -> Dict[str, Any]:
        """Calculate user interaction velocity and pacing."""
        timing = self._analyze_timing_patterns()

        if "error" in timing:
            return timing

        total_duration = timing["total_duration_seconds"]
        total_interactions = timing["total_interactions"]

        # Calculate velocity metrics
        interactions_per_second = total_interactions / total_duration if total_duration > 0 else 0
        interactions_per_minute = interactions_per_second * 60

        # Velocity classification
        if interactions_per_minute > 20:
            velocity_class = "Very Fast"
        elif interactions_per_minute > 12:
            velocity_class = "Fast"
        elif interactions_per_minute > 6:
            velocity_class = "Moderate"
        elif interactions_per_minute > 3:
            velocity_class = "Slow"
        else:
            velocity_class = "Very Slow"

        return {
            "interactions_per_second": round(interactions_per_second, 2),
            "interactions_per_minute": round(interactions_per_minute, 1),
            "velocity_classification": velocity_class,
            "pacing_consistency": self._assess_pacing_consistency(timing["interaction_delays"])
        }

    def _analyze_decision_patterns(self) -> Dict[str, Any]:
        """Analyze user decision-making patterns."""
        timing = self._analyze_timing_patterns()

        if "error" in timing:
            return timing

        delays = timing["interaction_delays"]

        # Identify decision points (longer delays indicate more thinking)
        avg_delay = timing["average_delay"]
        decision_threshold = avg_delay * 1.5  # 1.5x average is considered a decision point

        decision_points = []
        quick_decisions = []

        for i, delay in enumerate(delays):
            if delay > decision_threshold:
                decision_points.append({
                    "interaction_number": i + 1,
                    "delay_seconds": delay,
                    "decision_type": self._classify_decision_complexity(delay, avg_delay)
                })
            elif delay < avg_delay * 0.5:  # Quick decisions
                quick_decisions.append({
                    "interaction_number": i + 1,
                    "delay_seconds": delay
                })

        return {
            "decision_points": decision_points,
            "quick_decisions": quick_decisions,
            "decision_making_style": self._classify_decision_style(delays, avg_delay),
            "hesitation_indicators": len(decision_points),
            "confidence_indicators": len(quick_decisions)
        }

    def _calculate_engagement_score(self) -> Dict[str, Any]:
        """Calculate user engagement score based on interaction patterns."""
        timing = self._analyze_timing_patterns()

        if "error" in timing:
            return {"engagement_score": 0, "engagement_level": "Unknown"}

        # Factors for engagement scoring
        total_duration = timing["total_duration_seconds"]
        total_interactions = timing["total_interactions"]
        delay_variance = timing["delay_variance"]

        # Base score from interaction density
        interaction_density = total_interactions / total_duration if total_duration > 0 else 0
        density_score = min(interaction_density * 10, 40)  # Max 40 points

        # Consistency score (lower variance = higher consistency = higher engagement)
        max_variance = max(timing["interaction_delays"]) if timing["interaction_delays"] else 1
        consistency_score = max(0, 30 - (delay_variance / max_variance * 30)) if max_variance > 0 else 30

        # Completion score (completing the flow indicates engagement)
        completion_score = 30  # Assume completion since we have the full flow

        total_score = density_score + consistency_score + completion_score

        # Normalize to 0-100 scale
        engagement_score = min(total_score, 100)

        # Classify engagement level
        if engagement_score >= 80:
            engagement_level = "High"
        elif engagement_score >= 60:
            engagement_level = "Moderate"
        elif engagement_score >= 40:
            engagement_level = "Low"
        else:
            engagement_level = "Very Low"

        return {
            "engagement_score": round(engagement_score, 1),
            "engagement_level": engagement_level,
            "score_breakdown": {
                "interaction_density": round(density_score, 1),
                "consistency": round(consistency_score, 1),
                "completion": completion_score
            }
        }

    def _assess_user_confidence(self) -> Dict[str, Any]:
        """Assess user confidence based on interaction patterns."""
        timing = self._analyze_timing_patterns()

        if "error" in timing:
            return {"confidence_level": "Unknown"}

        delays = timing["interaction_delays"]
        avg_delay = timing["average_delay"]

        # Confidence indicators
        quick_actions = len([d for d in delays if d < avg_delay * 0.5])
        hesitation_points = len([d for d in delays if d > avg_delay * 2])

        # Calculate confidence score
        total_actions = len(delays)
        if total_actions == 0:
            return {"confidence_level": "Unknown"}

        quick_ratio = quick_actions / total_actions
        hesitation_ratio = hesitation_points / total_actions

        confidence_score = (quick_ratio * 100) - (hesitation_ratio * 50)
        confidence_score = max(0, min(100, confidence_score))

        # Classify confidence level
        if confidence_score >= 75:
            confidence_level = "High"
        elif confidence_score >= 50:
            confidence_level = "Moderate"
        elif confidence_score >= 25:
            confidence_level = "Low"
        else:
            confidence_level = "Very Low"

        return {
            "confidence_score": round(confidence_score, 1),
            "confidence_level": confidence_level,
            "quick_actions": quick_actions,
            "hesitation_points": hesitation_points,
            "confidence_indicators": {
                "decisive_actions": quick_actions,
                "uncertain_moments": hesitation_points,
                "consistency": 100 - timing["delay_variance"]
            }
        }

    def _measure_journey_efficiency(self) -> Dict[str, Any]:
        """Measure how efficiently the user completed their journey."""
        timing = self._analyze_timing_patterns()

        if "error" in timing:
            return {"efficiency_score": 0}

        total_duration = timing["total_duration_seconds"]
        total_interactions = timing["total_interactions"]

        # Estimate optimal completion time (assuming expert user)
        # Base estimate: 1-2 seconds per interaction for an expert
        estimated_optimal_time = total_interactions * 1.5

        # Calculate efficiency
        if total_duration > 0:
            efficiency_ratio = estimated_optimal_time / total_duration
            efficiency_score = min(efficiency_ratio * 100, 100)
        else:
            efficiency_score = 0

        # Classify efficiency
        if efficiency_score >= 80:
            efficiency_level = "Highly Efficient"
        elif efficiency_score >= 60:
            efficiency_level = "Efficient"
        elif efficiency_score >= 40:
            efficiency_level = "Moderately Efficient"
        else:
            efficiency_level = "Inefficient"

        return {
            "efficiency_score": round(efficiency_score, 1),
            "efficiency_level": efficiency_level,
            "actual_time": total_duration,
            "estimated_optimal_time": estimated_optimal_time,
            "time_difference": round(total_duration - estimated_optimal_time, 1)
        }

    def _generate_behavior_insights(self) -> List[str]:
        """Generate human-readable insights about user behavior."""
        insights = []

        # Get analysis results
        timing = self._analyze_timing_patterns()
        if "error" in timing:
            return ["Unable to generate behavioral insights due to insufficient data"]

        velocity = self._calculate_interaction_velocity()
        decisions = self._analyze_decision_patterns()
        engagement = self._calculate_engagement_score()
        confidence = self._assess_user_confidence()
        efficiency = self._measure_journey_efficiency()

        # Generate insights based on analysis
        avg_delay = timing["average_delay"]

        # Timing insights
        if avg_delay > 5:
            insights.append(f"User took time to consider options (average {avg_delay}s between actions)")
        elif avg_delay < 2:
            insights.append(f"User moved quickly through the flow ({avg_delay}s average between actions)")

        # Decision pattern insights
        if decisions["hesitation_indicators"] > 2:
            insights.append("Multiple decision points detected - user carefully evaluated options")

        if decisions["confidence_indicators"] > 3:
            insights.append("User showed confidence with quick successive actions")

        # Engagement insights
        engagement_level = engagement["engagement_level"]
        insights.append(f"User engagement level: {engagement_level} ({engagement['engagement_score']:.0f}/100)")

        # Confidence insights
        confidence_level = confidence["confidence_level"]
        if confidence_level in ["High", "Moderate"]:
            insights.append(f"User demonstrated {confidence_level.lower()} confidence in their choices")

        # Efficiency insights
        efficiency_level = efficiency["efficiency_level"]
        insights.append(f"Journey completion was {efficiency_level.lower()}")

        return insights

    def _classify_interaction_tempo(self, delays: List[float]) -> str:
        """Classify the overall tempo of user interactions."""
        avg_delay = statistics.mean(delays)

        if avg_delay < 1.5:
            return "Rapid"
        elif avg_delay < 3:
            return "Steady"
        elif avg_delay < 6:
            return "Deliberate"
        else:
            return "Contemplative"

    def _classify_decision_complexity(self, delay: float, avg_delay: float) -> str:
        """Classify the complexity of a decision based on delay time."""
        if delay > avg_delay * 3:
            return "Complex Decision"
        elif delay > avg_delay * 2:
            return "Moderate Decision"
        else:
            return "Simple Decision"

    def _classify_decision_style(self, delays: List[float], avg_delay: float) -> str:
        """Classify the user's overall decision-making style."""
        quick_decisions = len([d for d in delays if d < avg_delay * 0.5])
        slow_decisions = len([d for d in delays if d > avg_delay * 1.5])
        total_decisions = len(delays)

        if total_decisions == 0:
            return "Unknown"

        quick_ratio = quick_decisions / total_decisions
        slow_ratio = slow_decisions / total_decisions

        if quick_ratio > 0.6:
            return "Decisive"
        elif slow_ratio > 0.4:
            return "Analytical"
        else:
            return "Balanced"

    def _assess_pacing_consistency(self, delays: List[float]) -> str:
        """Assess how consistent the user's pacing was."""
        if len(delays) < 2:
            return "Unknown"

        variance = statistics.variance(delays)
        mean_delay = statistics.mean(delays)

        # Coefficient of variation
        cv = variance / mean_delay if mean_delay > 0 else 0

        if cv < 0.3:
            return "Very Consistent"
        elif cv < 0.6:
            return "Consistent"
        elif cv < 1.0:
            return "Somewhat Variable"
        else:
            return "Highly Variable"

    def _analyze_interaction_precision(self) -> Dict[str, Any]:
        """
        Analyze the precision and patterns of user interactions based on coordinates.

        Returns:
            Dictionary containing precision analytics results
        """
        click_events = [e for e in self.captured_events if e.get("type") == "click" and "frameX" in e and "frameY" in e]

        if len(click_events) < 2:
            return {"error": "Insufficient click events with coordinates for precision analysis"}

        # Extract coordinate data
        coordinates = [(e["frameX"], e["frameY"]) for e in click_events]
        times = [e["timeMs"] for e in click_events]

        # Calculate movement distances and patterns
        movement_distances = []
        movement_velocities = []
        click_regions = []

        for i in range(1, len(coordinates)):
            # Calculate distance between consecutive clicks
            x1, y1 = coordinates[i-1]
            x2, y2 = coordinates[i]
            distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            movement_distances.append(distance)

            # Calculate movement velocity (pixels per second)
            time_diff = (times[i] - times[i-1]) / 1000  # Convert to seconds
            if time_diff > 0:
                velocity = distance / time_diff
                movement_velocities.append(velocity)

            # Classify click regions
            click_regions.append(self._classify_click_region(x2, y2))

        # Calculate screen coverage and exploration
        x_coords = [c[0] for c in coordinates]
        y_coords = [c[1] for c in coordinates]
        screen_coverage = {
            "x_range": max(x_coords) - min(x_coords) if x_coords else 0,
            "y_range": max(y_coords) - min(y_coords) if y_coords else 0,
            "x_center": statistics.mean(x_coords) if x_coords else 0,
            "y_center": statistics.mean(y_coords) if y_coords else 0
        }

        # Analyze click clustering
        click_clusters = self._analyze_click_clustering(coordinates)

        # Movement efficiency analysis
        total_movement = sum(movement_distances)
        direct_distance = ((coordinates[-1][0] - coordinates[0][0])**2 +
                          (coordinates[-1][1] - coordinates[0][1])**2)**0.5 if len(coordinates) >= 2 else 0
        movement_efficiency = (direct_distance / total_movement * 100) if total_movement > 0 else 0

        return {
            "total_clicks": len(click_events),
            "movement_analysis": {
                "total_movement_distance": round(total_movement, 1),
                "average_movement_distance": round(statistics.mean(movement_distances), 1) if movement_distances else 0,
                "movement_efficiency": round(movement_efficiency, 1),
                "movement_pattern": self._classify_movement_pattern(movement_distances)
            },
            "velocity_analysis": {
                "average_movement_velocity": round(statistics.mean(movement_velocities), 1) if movement_velocities else 0,
                "max_movement_velocity": round(max(movement_velocities), 1) if movement_velocities else 0,
                "velocity_consistency": self._assess_velocity_consistency(movement_velocities)
            },
            "screen_usage": {
                "screen_coverage_x": round(screen_coverage["x_range"], 1),
                "screen_coverage_y": round(screen_coverage["y_range"], 1),
                "interaction_center": (round(screen_coverage["x_center"], 1), round(screen_coverage["y_center"], 1)),
                "screen_exploration": self._classify_screen_exploration(screen_coverage)
            },
            "click_patterns": {
                "click_regions": click_regions,
                "clustering_analysis": click_clusters,
                "precision_score": self._calculate_precision_score(movement_distances, movement_velocities)
            },
            "precision_insights": self._generate_precision_insights(movement_distances, movement_velocities, screen_coverage, click_regions)
        }

    def _classify_click_region(self, x: float, y: float) -> str:
        """Classify click location into general screen regions."""
        # Assume standard screen dimensions for classification
        # These thresholds can be adjusted based on actual screen size data
        if y < 100:
            return "header"
        elif y > 600:
            return "footer"
        elif x < 300:
            return "left_sidebar"
        elif x > 1200:
            return "right_sidebar"
        else:
            return "main_content"

    def _analyze_click_clustering(self, coordinates: list) -> Dict[str, Any]:
        """Analyze clustering patterns in click coordinates."""
        if len(coordinates) < 3:
            return {"cluster_count": len(coordinates), "clustering_type": "insufficient_data"}

        # Simple clustering analysis - group clicks within 100px radius
        clusters = []
        cluster_threshold = 100  # pixels

        for coord in coordinates:
            placed = False
            for cluster in clusters:
                # Check if coordinate is within threshold of cluster center
                cluster_center_x = statistics.mean([c[0] for c in cluster])
                cluster_center_y = statistics.mean([c[1] for c in cluster])
                distance = ((coord[0] - cluster_center_x)**2 + (coord[1] - cluster_center_y)**2)**0.5

                if distance <= cluster_threshold:
                    cluster.append(coord)
                    placed = True
                    break

            if not placed:
                clusters.append([coord])

        return {
            "cluster_count": len(clusters),
            "largest_cluster_size": max(len(cluster) for cluster in clusters) if clusters else 0,
            "clustering_type": self._classify_clustering_type(len(clusters), len(coordinates))
        }

    def _classify_clustering_type(self, cluster_count: int, total_clicks: int) -> str:
        """Classify the type of clustering pattern."""
        if cluster_count == 1:
            return "highly_focused"
        elif cluster_count <= total_clicks * 0.3:
            return "focused"
        elif cluster_count <= total_clicks * 0.6:
            return "moderate_spread"
        else:
            return "widely_distributed"

    def _classify_movement_pattern(self, distances: list) -> str:
        """Classify the overall movement pattern."""
        if not distances:
            return "no_movement"

        avg_distance = statistics.mean(distances)
        if avg_distance < 100:
            return "minimal_movement"
        elif avg_distance < 300:
            return "focused_movement"
        elif avg_distance < 600:
            return "moderate_movement"
        else:
            return "extensive_movement"

    def _assess_velocity_consistency(self, velocities: list) -> str:
        """Assess consistency of movement velocities."""
        if len(velocities) < 2:
            return "insufficient_data"

        cv = statistics.variance(velocities) / statistics.mean(velocities) if statistics.mean(velocities) > 0 else 0

        if cv < 0.5:
            return "very_consistent"
        elif cv < 1.0:
            return "consistent"
        elif cv < 2.0:
            return "variable"
        else:
            return "highly_variable"

    def _classify_screen_exploration(self, screen_coverage: Dict) -> str:
        """Classify the level of screen exploration."""
        x_range = screen_coverage["x_range"]
        y_range = screen_coverage["y_range"]
        total_coverage = (x_range * y_range) ** 0.5  # Geometric mean of coverage

        if total_coverage < 200:
            return "minimal_exploration"
        elif total_coverage < 500:
            return "focused_exploration"
        elif total_coverage < 1000:
            return "moderate_exploration"
        else:
            return "extensive_exploration"

    def _calculate_precision_score(self, distances: list, velocities: list) -> float:
        """Calculate an overall precision score (0-100)."""
        if not distances or not velocities:
            return 0

        # Lower average distance = higher precision
        avg_distance = statistics.mean(distances)
        distance_score = max(0, 100 - (avg_distance / 10))  # Scale factor

        # More consistent velocities = higher precision
        velocity_consistency = statistics.variance(velocities) / statistics.mean(velocities) if statistics.mean(velocities) > 0 else 0
        consistency_score = max(0, 100 - (velocity_consistency * 20))  # Scale factor

        # Combine scores
        precision_score = (distance_score * 0.6 + consistency_score * 0.4)
        return round(min(100, max(0, precision_score)), 1)

    def _generate_precision_insights(self, distances: list, velocities: list, screen_coverage: Dict, regions: list) -> list:
        """Generate human-readable insights about interaction precision."""
        insights = []

        if distances:
            avg_distance = statistics.mean(distances)
            if avg_distance < 150:
                insights.append("User demonstrated precise, focused interactions with minimal cursor movement")
            elif avg_distance > 500:
                insights.append("User exhibited broad screen navigation with extensive cursor movements")

        if velocities:
            avg_velocity = statistics.mean(velocities)
            if avg_velocity > 1000:
                insights.append("User moved quickly between interaction points, indicating confidence or urgency")
            elif avg_velocity < 200:
                insights.append("User moved deliberately and carefully between interactions")

        # Analyze screen exploration
        total_coverage = (screen_coverage["x_range"] * screen_coverage["y_range"]) ** 0.5
        if total_coverage > 800:
            insights.append("User explored multiple areas of the interface comprehensively")
        elif total_coverage < 300:
            insights.append("User remained focused within a specific interface area")

        # Analyze interaction regions
        if regions:
            main_content_clicks = regions.count("main_content")
            if main_content_clicks / len(regions) > 0.8:
                insights.append("User primarily focused on main content area, indicating clear task orientation")

        return insights