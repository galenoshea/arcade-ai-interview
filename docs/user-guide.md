# User Guide

## Overview
The Arcade Flow Analyzer is a professional-grade tool that transforms Arcade flow recordings into comprehensive, AI-powered analysis reports.

## Features
- **User Interaction Analysis**: Human-readable extraction of user actions
- **AI-Powered Insights**: GPT-4o analysis of user intent and behavior
- **Visual Analysis**: GPT-4o Vision analyzes screenshots for UI/UX insights
- **Social Media Generation**: Adaptive DALL-E 3 image creation
- **Cost Optimization**: Intelligent model selection and API caching
- **Comprehensive Reports**: Professional markdown documentation

## Installation

### Prerequisites
- Python 3.10 or higher
- Poetry (recommended) or pip
- OpenAI API key

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd arcade-ai-interview
   ```

2. **Install dependencies:**
   ```bash
   # Using Poetry (recommended)
   poetry install

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env with your OpenAI API key
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Prepare your data:**
   ```bash
   # Place your Flow.json file in the data/raw/ directory
   cp your-flow.json data/raw/Flow.json
   ```

## Usage

### Basic Usage

Run the analyzer with default settings:

```bash
# Using Poetry
poetry run python -m src.arcade_flow_analyzer.main

# Or direct Python
python -m src.arcade_flow_analyzer.main
```

### Expected Output

The analyzer will generate:

1. **Comprehensive Report**: `results/flow_analysis_report.md`
2. **Social Media Image**: `results/social_media_image.png`
3. **Console Summary**: Cost and performance metrics

### Sample Output Structure

```
results/
├── flow_analysis_report.md    # Main analysis report
└── social_media_image.png     # Generated social media asset
```

## Report Sections

### 1. Executive Summary
- Generated timestamp
- Flow name and type
- High-level summary of user accomplishments

### 2. User Journey Analysis
- Primary user goal identification
- Flow metadata (steps, use case, AI processing)
- Key behavioral insights

### 3. User Interactions Breakdown
- Chronological list of user actions
- Human-readable descriptions
- Page context information

### 4. Page Navigation Flow
- URLs visited during the journey
- Page titles and transitions
- Navigation efficiency analysis

### 5. Visual Design Analysis
- Application type identification (e-commerce, social media, etc.)
- Visual style assessment (modern, classic, minimal)
- Brand color detection
- UI pattern recognition
- Design quality insights

### 6. Technical Details
- Flow statistics and metrics
- Quality assessment
- Performance indicators

### 7. Social Media Asset
- Generated image embedded in report
- Professional quality for marketing use

## Configuration Options

### Environment Variables

Create a `.env` file with the following options:

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional (with defaults)
LOG_LEVEL=INFO
CACHE_DIR=.cache
RESULTS_DIR=results
```

### Directory Structure

The analyzer expects this structure:

```
project/
├── data/
│   └── raw/
│       └── Flow.json          # Your Arcade flow data
├── results/                   # Generated reports (auto-created)
├── .cache/                    # API response cache (auto-created)
├── logs/                      # Application logs (auto-created)
└── .env                       # Your configuration
```

## Advanced Features

### Cost Optimization

The analyzer includes intelligent cost optimization:

- **Caching**: API responses are cached to avoid redundant calls
- **Model Tiers**: Automatically selects cheaper models for simple tasks
- **Usage Tracking**: Provides cost breakdown after each run

### Visual Analysis

Enhanced with GPT-4o Vision capabilities:

- Analyzes actual screenshots from the flow
- Identifies UI patterns and design elements
- Detects brand colors and visual style
- Provides UX quality assessment

### Adaptive Image Generation

DALL-E 3 prompts adapt based on visual analysis:

- Uses detected brand colors in generated images
- Matches the application's visual style
- Incorporates identified UI patterns
- Creates contextually relevant social media content

## Troubleshooting

### Common Issues

#### 1. Missing API Key
```
ERROR: OpenAI API key is required
```
**Solution**: Add your API key to `.env` file

#### 2. Missing Flow File
```
ERROR: File not found: data/raw/Flow.json
```
**Solution**: Place your Flow.json file in `data/raw/` directory

#### 3. API Rate Limits
```
ERROR: Rate limit exceeded
```
**Solution**: The analyzer includes intelligent caching. Wait and retry.

#### 4. Insufficient API Credits
```
ERROR: You exceeded your current quota
```
**Solution**: Check your OpenAI account billing and add credits

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Run with debug output
poetry run python -m src.arcade_flow_analyzer.main
```

### Cache Management

Clear cache to force fresh API calls:

```bash
# Remove cache directory
rm -rf .cache/

# Or use the clean script
./scripts/clean.sh
```

## Performance Tips

1. **Use Caching**: Keep the `.cache/` directory to avoid redundant API calls
2. **Monitor Costs**: Check the cost summary after each run
3. **Batch Processing**: Analyze multiple flows in sequence to benefit from caching
4. **Log Management**: Regularly clean the `logs/` directory

## Flow Requirements

### Supported Flow Types

The analyzer works with Arcade flows containing:

- **IMAGE steps**: Screenshots with user interaction hotspots
- **CHAPTER steps**: Titles and context information (extracted for context)
- **VIDEO steps**: Currently logged but not processed

### Optimal Flow Structure

For best results, ensure your Arcade flow includes:

- Clear user interaction points (clicks, taps, inputs)
- High-quality screenshots
- Descriptive step labels
- Logical progression through the user journey

### Flow Data Format

Expected JSON structure:
```json
{
  "name": "Flow Name",
  "description": "Flow description",
  "useCase": "promotional|tutorial|demo",
  "schemaVersion": "1.1.0",
  "steps": [
    {
      "type": "IMAGE",
      "id": "step-id",
      "url": "screenshot-url",
      "hotspots": [
        {
          "x": 100,
          "y": 200,
          "label": "Click here"
        }
      ],
      "pageContext": {
        "title": "Page Title",
        "url": "https://example.com"
      }
    }
  ]
}
```

## Integration

### CI/CD Integration

Add to your workflow:

```yaml
- name: Analyze Flow
  run: |
    poetry install
    poetry run python -m src.arcade_flow_analyzer.main

- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: flow-analysis
    path: results/
```

### API Integration

Use as a library:

```python
from arcade_flow_analyzer.main import main
from arcade_flow_analyzer.parser import FlowParser
import json

# Load and analyze programmatically
with open("data/raw/Flow.json") as f:
    flow_data = json.load(f)

parser = FlowParser(flow_data)
interactions = parser.extract_user_interactions()
```

## Support

For issues and questions:

1. Check this documentation
2. Review the [API Reference](./api-reference.md)
3. Check the [Architecture Overview](./architecture.md)
4. Review logs in the `logs/` directory

## License

This project is created for the Arcade AI Interview Challenge.