# API Reference

## Module Documentation

### arcade_flow_analyzer.main

Main orchestration module for the Arcade Flow Analyzer.

#### Functions

##### `main() -> int`
Main execution function that orchestrates the complete flow analysis workflow.

**Returns:**
- `int`: Exit code (0 for success, 1 for error)

**Workflow:**
1. Configuration validation and setup
2. Flow data loading and parsing
3. AI-powered analysis (text + visual)
4. Social media image generation
5. Comprehensive report generation

**Example:**
```python
from arcade_flow_analyzer.main import main
exit_code = main()
```

---

### arcade_flow_analyzer.config

Configuration management and environment setup.

#### Classes

##### `Config`
Centralized configuration management class.

**Attributes:**
- `FLOW_FILE` (Path): Path to the Flow.json file
- `OPENAI_API_KEY` (str): OpenAI API key from environment
- `RESULTS_DIR` (Path): Output directory for results
- `CACHE_DIR` (Path): Cache directory for API responses
- `LOG_LEVEL` (str): Logging level configuration

**Methods:**

###### `validate() -> None`
Validates all configuration parameters and raises ValueError if invalid.

**Raises:**
- `ValueError`: If required configuration is missing or invalid

###### `setup_logging() -> None`
Configures logging for the application.

###### `display_info() -> None`
Displays configuration information for debugging.

#### Functions

##### `get_config() -> Config`
Returns the singleton configuration instance.

**Returns:**
- `Config`: Configured instance

---

### arcade_flow_analyzer.parser

Flow data parsing and extraction utilities.

#### Classes

##### `FlowParser`
Parses and extracts meaningful information from Arcade flow data.

**Constructor:**
```python
FlowParser(flow_data: Dict[str, Any])
```

**Parameters:**
- `flow_data`: The raw flow data dictionary from JSON file

**Methods:**

###### `extract_user_interactions() -> List[Dict[str, Any]]`
Extract and format user interactions from the flow data.

**Returns:**
- `List[Dict]`: List of interaction dictionaries with structured data

**Interaction Structure:**
```python
{
    "step_id": str,
    "action_type": str,
    "description": str,
    "url": str,
    "page_title": str,
    "element_type": str,
    "element_text": str,
    "css_selector": str,
    "coordinates": {"x": int, "y": int},
    "screenshot_url": str,
    "original_screenshot_url": str
}
```

###### `get_flow_summary() -> Dict[str, Any]`
Generate a summary of the flow metadata.

**Returns:**
- `Dict`: Flow summary information

**Summary Structure:**
```python
{
    "name": str,
    "description": str,
    "use_case": str,
    "total_steps": int,
    "has_ai_processing": bool,
    "created": dict,
    "schema_version": str
}
```

###### `analyze_user_journey() -> Dict[str, Any]`
Analyze the complete user journey through the flow.

**Returns:**
- `Dict`: Journey analysis data including page transitions and key actions

###### `extract_screenshots() -> List[Dict[str, Any]]`
Extract all screenshots from the flow for visual analysis.

**Returns:**
- `List[Dict]`: Screenshot dictionaries with metadata

---

### arcade_flow_analyzer.analyzer

AI-powered analysis using OpenAI's GPT-4 and DALL-E.

#### Classes

##### `AIAnalyzer`
Handles AI-powered analysis using OpenAI's models.

**Constructor:**
```python
AIAnalyzer(api_key: Optional[str] = None)
```

**Parameters:**
- `api_key`: Optional OpenAI API key (uses config default if not provided)

**Class Attributes:**

###### `ANALYSIS_SCHEMA`
JSON Schema for structured outputs ensuring 100% JSON compliance.

###### `MODEL_TIERS`
Tiered model configuration for cost optimization:
- `premium`: GPT-4o for complex analysis
- `standard`: GPT-3.5-turbo for simple tasks
- `vision`: GPT-4o for visual analysis

**Methods:**

###### `analyze_user_intent(interactions: List[Dict], flow_summary: Dict, visual_analysis: Optional[Dict] = None) -> Dict[str, str]`
Use GPT-4 to analyze user intent and generate human-readable descriptions.

**Parameters:**
- `interactions`: List of user interactions
- `flow_summary`: Flow metadata summary
- `visual_analysis`: Optional visual analysis results

**Returns:**
- `Dict`: Analysis results with summary, user_goal, and key_insights

###### `analyze_screenshots(screenshots: List[Dict], interactions: List[Dict]) -> Dict[str, Any]`
Analyze screenshots using GPT-4 Vision to understand visual context.

**Parameters:**
- `screenshots`: List of screenshot metadata with URLs
- `interactions`: List of user interactions for context

**Returns:**
- `Dict`: Visual analysis results including UI patterns and design insights

###### `generate_social_media_image(flow_summary: Dict, analysis: Dict, visual_analysis: Optional[Dict] = None) -> Optional[str]`
Generate a social media image using DALL-E 3.

**Parameters:**
- `flow_summary`: Flow metadata summary
- `analysis`: Analysis results
- `visual_analysis`: Optional visual analysis for adaptive prompts

**Returns:**
- `Optional[str]`: Path to generated image file, or None if failed

###### `get_cost_summary() -> Dict`
Get a summary of API costs and usage statistics.

**Returns:**
- `Dict`: Cost breakdown and optimization insights

---

### arcade_flow_analyzer.cache

API response caching for cost optimization.

#### Classes

##### `CacheManager`
Manages persistent caching of API responses.

**Constructor:**
```python
CacheManager(cache_dir: Optional[Path] = None)
```

**Parameters:**
- `cache_dir`: Optional cache directory path

**Methods:**

###### `get(key: str) -> Optional[Any]`
Retrieve cached data by key.

**Parameters:**
- `key`: Cache key

**Returns:**
- `Optional[Any]`: Cached data or None if not found

###### `set(key: str, data: Any) -> None`
Store data in cache with the given key.

**Parameters:**
- `key`: Cache key
- `data`: Data to cache

###### `_get_cache_key(data: str) -> str`
Generate MD5 cache key from input data.

**Parameters:**
- `data`: Input data string

**Returns:**
- `str`: MD5 hash as cache key

---

### arcade_flow_analyzer.reporter

Comprehensive markdown report generation.

#### Classes

##### `ReportGenerator`
Generates comprehensive markdown reports.

**Constructor:**
```python
ReportGenerator(output_dir: Optional[Path] = None)
```

**Parameters:**
- `output_dir`: Optional output directory path

**Methods:**

###### `generate_markdown_report(flow_summary: Dict, interactions: List[Dict], analysis: Dict, journey_analysis: Dict, image_path: Optional[str] = None, visual_analysis: Optional[Dict] = None) -> str`
Generate a comprehensive markdown report.

**Parameters:**
- `flow_summary`: Flow metadata summary
- `interactions`: List of user interactions
- `analysis`: AI analysis results
- `journey_analysis`: User journey analysis
- `image_path`: Optional path to generated social media image
- `visual_analysis`: Optional visual analysis results

**Returns:**
- `str`: Path to the generated report file

###### `generate_summary_report(flow_summary: Dict, interactions: List[Dict], analysis: Dict) -> str`
Generate a brief summary report for quick overview.

**Parameters:**
- `flow_summary`: Flow metadata summary
- `interactions`: List of user interactions
- `analysis`: AI analysis results

**Returns:**
- `str`: Path to the generated summary report file

## Error Handling

All modules implement comprehensive error handling:

- **FileNotFoundError**: When Flow.json is missing
- **ValueError**: For configuration errors
- **OpenAI API Errors**: Graceful degradation with fallback responses
- **Network Errors**: Retry logic with exponential backoff

## Usage Examples

### Basic Usage
```python
from arcade_flow_analyzer.main import main

# Run complete analysis
exit_code = main()
```

### Component Usage
```python
from arcade_flow_analyzer.parser import FlowParser
from arcade_flow_analyzer.analyzer import AIAnalyzer
import json

# Load flow data
with open("data/Flow.json", "r") as f:
    flow_data = json.load(f)

# Parse interactions
parser = FlowParser(flow_data)
interactions = parser.extract_user_interactions()
flow_summary = parser.get_flow_summary()

# Analyze with AI
analyzer = AIAnalyzer()
analysis = analyzer.analyze_user_intent(interactions, flow_summary)
```

### Configuration
```python
from arcade_flow_analyzer.config import get_config

config = get_config()
config.validate()
print(f"Output directory: {config.RESULTS_DIR}")
```