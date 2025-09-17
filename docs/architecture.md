# Architecture Overview

## System Architecture

The Arcade Flow Analyzer follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     Main Orchestrator                    │
│                    (main.py)                            │
└─────────────┬───────────────────────────────┬──────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│     Flow Parser         │     │     AI Analyzer         │
│    (parser.py)         │     │    (analyzer.py)        │
│                        │     │                         │
│ • Extract interactions │     │ • GPT-4o Analysis      │
│ • Parse flow metadata  │     │ • Vision Analysis      │
│ • Extract screenshots  │     │ • DALL-E Generation    │
└─────────────────────────┘     └─────────────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    Cache Manager        │     │   Report Generator      │
│    (cache.py)          │     │    (reporter.py)        │
│                        │     │                         │
│ • API Response Cache   │     │ • Markdown Generation   │
│ • Cost Optimization    │     │ • Visual Integration    │
└─────────────────────────┘     └─────────────────────────┘
```

## Core Components

### 1. Main Orchestrator (`main.py`)
**Responsibility**: Coordinates the entire analysis workflow

**Key Functions**:
- `main()`: Primary execution function
- Loads and validates configuration
- Orchestrates component interaction
- Handles error recovery

### 2. Configuration Manager (`config.py`)
**Responsibility**: Centralized configuration and environment management

**Features**:
- Environment variable loading
- Directory structure management
- Logging configuration
- API key validation

### 3. Flow Parser (`parser.py`)
**Responsibility**: Extracts meaningful data from Arcade flow JSON

**Methods**:
- `extract_user_interactions()`: Extracts user click actions
- `get_flow_summary()`: Generates flow metadata
- `analyze_user_journey()`: Analyzes page transitions
- `extract_screenshots()`: Collects screenshot URLs

### 4. AI Analyzer (`analyzer.py`)
**Responsibility**: AI-powered analysis and content generation

**Key Features**:
- **Multi-modal Analysis**: GPT-4o Vision for screenshots
- **Structured Outputs**: 100% JSON compliance
- **Tiered Models**: Cost optimization through intelligent model selection
- **Adaptive Generation**: Context-aware DALL-E prompts

**Methods**:
- `analyze_user_intent()`: Generates user goal and insights
- `analyze_screenshots()`: Visual analysis with GPT-4o Vision
- `generate_social_media_image()`: Creates engaging social images
- `_select_model_tier()`: Intelligent model routing

### 5. Cache Manager (`cache.py`)
**Responsibility**: API response caching for cost optimization

**Features**:
- MD5-based cache key generation
- JSON serialization
- File-based persistent cache
- Automatic cache directory management

### 6. Report Generator (`reporter.py`)
**Responsibility**: Comprehensive markdown report generation

**Sections Generated**:
- Executive Summary
- User Journey Analysis
- Visual Design Analysis
- Technical Details
- Social Media Asset Integration

## Data Flow

1. **Input**: `Flow.json` from Arcade recording
2. **Parsing**: Extract interactions, screenshots, metadata
3. **Analysis**:
   - Visual analysis of screenshots (GPT-4o Vision)
   - User intent analysis (GPT-4o with structured outputs)
   - Combined insights generation
4. **Generation**:
   - Adaptive social media image (DALL-E 3)
   - Comprehensive markdown report
5. **Output**:
   - `flow_analysis_report.md`
   - `social_media_image.png`

## Technology Stack

### Core Technologies
- **Python 3.10**: Primary programming language
- **Poetry**: Dependency management
- **OpenAI API**: AI analysis and generation

### AI Models
- **GPT-4o**: Complex analysis and vision capabilities
- **GPT-3.5-turbo**: Standard analysis (cost optimization)
- **DALL-E 3**: Social media image generation

### Key Libraries
- **openai**: OpenAI API client
- **python-dotenv**: Environment variable management
- **pytest**: Testing framework
- **flake8**: Code quality enforcement

## Design Patterns

### 1. Modular Architecture
Each component has a single responsibility and clear interfaces.

### 2. Dependency Injection
Components receive dependencies through constructors for flexibility.

### 3. Caching Strategy
Expensive API calls are cached to reduce costs and improve performance.

### 4. Configuration Singleton
Centralized configuration management through the Config class.

### 5. Error Recovery
Graceful degradation when API calls fail with fallback responses.

## Security Considerations

1. **API Key Protection**: Stored in `.env` file, never committed
2. **Input Validation**: Flow data validated before processing
3. **Cache Security**: No sensitive data in cache keys
4. **Error Handling**: No sensitive information in error messages

## Performance Optimizations

1. **Intelligent Caching**: MD5-based cache keys for API responses
2. **Tiered Model Selection**: Use cheaper models when appropriate
3. **Batch Processing**: Analyze multiple screenshots together
4. **Early Returns**: Cache hits bypass expensive operations

## Extensibility Points

1. **New Step Types**: Extend parser to handle VIDEO, CHAPTER steps
2. **Additional AI Models**: Add support for other AI providers
3. **Report Formats**: Generate HTML, PDF, or other formats
4. **Analysis Plugins**: Add specialized analysis modules
5. **Export Options**: Integration with external systems