# Arcade Flow Analyzer

A professional AI-powered analysis tool for Arcade flow recordings that generates comprehensive reports and social media content.

## Features

- **AI-Powered Analysis**: Uses OpenAI GPT-4 to analyze user intent and behavior patterns
- **Social Media Image Generation**: Creates engaging images with DALL-E 3 for social platforms
- **Intelligent Caching**: Reduces API costs with smart response caching
- **Professional Reporting**: Generates comprehensive markdown reports with insights
- **Modern Python Architecture**: Built with Poetry, src/ layout, and type hints

## Requirements

- Python 3.8.1+
- Poetry (for dependency management)
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd arcade-ai-interview
   ```

2. **Install dependencies with Poetry**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   - Copy the `.env` file and add your OpenAI API key
   - The `.env` file is already configured for this project

## Project Structure

```
arcade-ai-interview/
├── src/
│   └── arcade_flow_analyzer/     # Main application package
│       ├── __init__.py
│       └── main.py              # Core analysis logic
├── cache/                       # API response cache (gitignored)
├── output/                      # Generated reports and images
│   ├── flow_analysis_report.md  # Comprehensive analysis report
│   └── social_media_image.png   # Generated social media asset
├── .env                         # Environment variables (gitignored)
├── .gitignore                   # Git ignore rules
├── Flow.json                    # Input flow data
├── pyproject.toml              # Poetry configuration
└── README.md                   # Original challenge description
```

## Usage

### Command Line Interface

Run the analysis using Poetry:

```bash
# Using the poetry script
poetry run analyze-flow

# Or directly with the module
poetry run python -m arcade_flow_analyzer.main
```

### What It Does

1. **Parses Flow Data**: Extracts user interactions from `Flow.json`
2. **AI Analysis**: Uses GPT-4 to analyze user intent and generate insights
3. **Image Generation**: Creates a social media image with DALL-E 3
4. **Report Generation**: Produces a comprehensive markdown report

### Output Files

- **`output/flow_analysis_report.md`**: Complete analysis with user journey, insights, and technical details
- **`output/social_media_image.png`**: Professional social media image for engagement
- **`cache/`**: Cached API responses to reduce costs during development

## Key Features

### Intelligent Caching
- Caches expensive OpenAI API responses for 24 hours
- Significantly reduces development costs
- Automatic cache invalidation

### Professional Analysis
- Extracts user interactions with human-readable descriptions
- Analyzes user intent and behavior patterns
- Provides actionable insights for UX improvement

### Modern Python Architecture
- Follows Python packaging best practices with `src/` layout
- Uses Poetry for dependency management
- Type hints and professional code structure
- Comprehensive error handling and logging

## Example Output

The tool analyzes the Target.com scooter shopping flow and generates:

1. **User Journey Summary**: "User successfully navigated through Target website to search for, customize, and add a scooter to their cart..."

2. **Key Interactions**:
   - Search for "scooter"
   - Browse product options
   - Customize color selection
   - Add to cart
   - Decline protection plan
   - Review cart

3. **Professional Insights**: UX analysis, behavior patterns, and improvement recommendations

## Social Media Integration

Generates professional images suitable for:
- LinkedIn posts about UX analysis
- Twitter content about e-commerce flows
- Blog post featured images
- Case study presentations

## Security

- API keys stored in `.env` file (gitignored)
- No sensitive data committed to version control
- Secure handling of API responses

## Development

### Code Quality Tools

```bash
# Format code
poetry run black src/

# Lint code
poetry run flake8 src/

# Type checking
poetry run mypy src/

# Run tests (when available)
poetry run pytest
```

### Cache Management

Cache files are stored in `cache/` and automatically managed:
- 24-hour expiration
- Automatic cleanup
- Development-friendly cost optimization

## Production Ready

This solution demonstrates:
- **Professional code architecture**
- **Cost-effective API usage**
- **Comprehensive error handling**
- **Clean, maintainable code**
- **Modern Python practices**

## Interview Excellence

Key technical decisions showcased:

1. **Poetry over pip**: Modern dependency management
2. **src/ layout**: Professional Python project structure
3. **Intelligent caching**: Cost optimization and performance
4. **Comprehensive logging**: Production-ready observability
5. **Type hints**: Code quality and maintainability
6. **Modular design**: Separation of concerns and testability

---

Built for the Arcade AI Interview Challenge