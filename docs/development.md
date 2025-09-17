# Development Guide

## Development Setup

### Prerequisites
- Python 3.10 or higher
- Poetry for dependency management
- Git for version control
- OpenAI API key for testing

### Local Development Environment

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd arcade-ai-interview
   poetry install
   ```

2. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your development API key
   ```

3. **Install development dependencies:**
   ```bash
   poetry install --with dev
   ```

4. **Verify setup:**
   ```bash
   poetry run python -m src.arcade_flow_analyzer.main
   ```

## Development Workflow

### Code Quality Standards

The project maintains high code quality through:

1. **Code Formatting**: Automatic formatting with Black
2. **Linting**: Code quality enforcement with flake8
3. **Type Checking**: Static type analysis with mypy
4. **Testing**: Comprehensive test suite with pytest

### Running Quality Checks

```bash
# Run all quality checks
make test

# Individual checks
poetry run flake8 src/
poetry run pytest tests/
poetry run mypy src/
```

### Git Workflow

1. **Feature Development:**
   ```bash
   git checkout -b feature/your-feature-name
   # Develop your feature
   git add .
   git commit -m "Add feature description"
   git push origin feature/your-feature-name
   ```

2. **Code Review Process:**
   - Create pull request
   - Ensure all tests pass
   - Get code review approval
   - Merge to main

### Testing Strategy

#### Unit Tests
Located in `tests/` directory with comprehensive coverage:

```bash
# Run tests with coverage
poetry run pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

#### Test Structure
```
tests/
├── test_parser.py      # FlowParser tests
├── test_analyzer.py    # AIAnalyzer tests
├── test_cache.py       # CacheManager tests
├── test_reporter.py    # ReportGenerator tests
├── test_config.py      # Config tests
└── fixtures/           # Test data
```

#### Testing Best Practices
- Mock external API calls
- Test both success and failure scenarios
- Use fixtures for test data
- Maintain >80% test coverage

### Project Structure

```
arcade-ai-interview/
├── src/
│   └── arcade_flow_analyzer/
│       ├── __init__.py
│       ├── main.py          # Main orchestrator
│       ├── config.py        # Configuration management
│       ├── parser.py        # Flow data parsing
│       ├── analyzer.py      # AI analysis
│       ├── cache.py         # Caching system
│       └── reporter.py      # Report generation
├── tests/                   # Test suite
├── docs/                    # Documentation
├── data/
│   └── raw/                 # Input data
├── results/                 # Generated outputs
├── logs/                    # Application logs
├── .cache/                  # API response cache
├── scripts/                 # Utility scripts
├── pyproject.toml          # Project configuration
├── README.md               # Project overview
└── .env                    # Environment variables
```

## Architecture Guidelines

### Design Principles

1. **Single Responsibility**: Each class has one clear purpose
2. **Dependency Injection**: Components receive dependencies
3. **Error Handling**: Graceful degradation with fallbacks
4. **Caching Strategy**: Expensive operations are cached
5. **Configuration Management**: Centralized config handling

### Code Organization

#### Module Responsibilities
- **main.py**: Workflow orchestration only
- **config.py**: Environment and configuration management
- **parser.py**: Flow data extraction and parsing
- **analyzer.py**: AI analysis and generation
- **cache.py**: Persistent caching system
- **reporter.py**: Output generation and formatting

#### Class Design Patterns
- **Singleton**: Configuration management
- **Strategy**: Model tier selection
- **Factory**: Report generation
- **Observer**: Cost tracking

### Adding New Features

#### 1. New Step Type Support

To add support for new Arcade step types:

```python
# In parser.py
def extract_video_interactions(self) -> List[Dict]:
    """Extract interactions from VIDEO steps."""
    interactions = []
    for step in self.steps:
        if step.get("type") == "VIDEO":
            # Process VIDEO step data
            pass
    return interactions
```

#### 2. New AI Model Integration

To add support for new AI models:

```python
# In analyzer.py
MODEL_TIERS = {
    "premium": {"model": "gpt-4o", ...},
    "standard": {"model": "gpt-3.5-turbo", ...},
    "vision": {"model": "gpt-4o", ...},
    "experimental": {"model": "new-model", ...}  # Add here
}
```

#### 3. New Report Formats

To add new report formats:

```python
# In reporter.py
def generate_html_report(self, ...) -> str:
    """Generate HTML format report."""
    # Implementation here
```

## API Development

### OpenAI Integration

#### Best Practices
1. **Error Handling**: Always wrap API calls in try-catch
2. **Rate Limiting**: Implement exponential backoff
3. **Cost Tracking**: Monitor token usage
4. **Caching**: Cache responses to reduce costs

#### Example API Call Pattern
```python
try:
    response = self.client.chat.completions.create(
        model=selected_model,
        messages=messages,
        max_tokens=1000,
        temperature=0.3
    )

    # Track costs
    tokens_used = response.usage.total_tokens
    self._track_api_cost(model_tier, tokens_used)

    # Cache response
    self.cache.set(cache_key, result)

    return result

except Exception as e:
    logger.error(f"API call failed: {e}")
    return fallback_response
```

### Structured Outputs

Using OpenAI's Structured Outputs for reliable JSON:

```python
response = self.client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "analysis_result",
            "schema": self.ANALYSIS_SCHEMA
        }
    }
)
```

## Performance Optimization

### Caching Strategy

1. **API Response Caching**: Cache expensive API calls
2. **Cache Key Generation**: Use MD5 hashes of input data
3. **Cache Invalidation**: Manual cache clearing when needed
4. **Cache Storage**: File-based persistent cache

### Cost Optimization

1. **Model Tier Selection**: Use cheaper models when appropriate
2. **Batch Processing**: Analyze multiple items together
3. **Token Management**: Optimize prompt lengths
4. **Usage Tracking**: Monitor and report costs

### Memory Management

1. **Lazy Loading**: Load data only when needed
2. **Resource Cleanup**: Properly dispose of resources
3. **Image Handling**: Optimize image processing
4. **Garbage Collection**: Ensure proper memory cleanup

## Debugging

### Logging Configuration

The application uses structured logging:

```python
import logging

logger = logging.getLogger(__name__)

# Different log levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
poetry run python -m src.arcade_flow_analyzer.main
```

### Common Debug Scenarios

1. **API Failures**: Check logs for API error details
2. **Cache Issues**: Clear cache and retry
3. **Flow Parsing**: Validate JSON structure
4. **Configuration**: Verify environment variables

## Contributing

### Code Style

Follow these conventions:

1. **Python Style**: PEP 8 compliance
2. **Naming**: Descriptive variable and function names
3. **Documentation**: Comprehensive docstrings
4. **Type Hints**: Use type annotations
5. **Comments**: Explain complex logic only

### Documentation

1. **Docstrings**: All public methods need docstrings
2. **Type Hints**: Use proper type annotations
3. **README Updates**: Update documentation for new features
4. **API Documentation**: Keep API reference current

### Pull Request Process

1. **Feature Branch**: Create from main
2. **Tests**: Add tests for new functionality
3. **Documentation**: Update relevant documentation
4. **Quality Checks**: Ensure all checks pass
5. **Review**: Get approval from maintainers

## Deployment

### Production Considerations

1. **Environment Variables**: Use production API keys
2. **Logging**: Configure appropriate log levels
3. **Caching**: Ensure cache directory permissions
4. **Error Handling**: Implement proper error recovery
5. **Monitoring**: Set up cost and performance monitoring

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY src/ ./src/
COPY data/ ./data/

CMD ["poetry", "run", "python", "-m", "src.arcade_flow_analyzer.main"]
```

### Environment Setup

```bash
# Production environment
export OPENAI_API_KEY=prod_key
export LOG_LEVEL=INFO
export CACHE_DIR=/app/cache
export RESULTS_DIR=/app/results
```

## Maintenance

### Regular Tasks

1. **Dependency Updates**: Keep dependencies current
2. **Security Patches**: Apply security updates promptly
3. **Performance Monitoring**: Track API costs and performance
4. **Log Rotation**: Manage log file sizes
5. **Cache Cleanup**: Periodic cache maintenance

### Monitoring

Track these metrics:

1. **API Costs**: Daily/monthly OpenAI usage
2. **Performance**: Analysis completion times
3. **Error Rates**: Failed analysis attempts
4. **Cache Hit Rates**: Caching effectiveness
5. **Resource Usage**: Memory and disk usage

### Troubleshooting Common Issues

1. **High API Costs**: Review caching effectiveness
2. **Slow Performance**: Check network and API latency
3. **Memory Issues**: Monitor large flow processing
4. **Cache Corruption**: Clear and rebuild cache
5. **Configuration Errors**: Validate all environment variables