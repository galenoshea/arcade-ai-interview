# Configuration Guide

## Overview
The Arcade Flow Analyzer uses environment-based configuration to maintain security and flexibility across different deployment environments.

## Environment Variables

### Required Configuration

#### `OPENAI_API_KEY`
**Description**: Your OpenAI API key for GPT-4o and DALL-E 3 access
**Type**: String
**Required**: Yes
**Example**: `sk-proj-...`
**Security**: Never commit this to version control

```bash
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
```

### Optional Configuration

#### `LOG_LEVEL`
**Description**: Controls logging verbosity
**Type**: String
**Default**: `INFO`
**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

```bash
LOG_LEVEL=INFO
```

**Log Level Behavior:**
- `DEBUG`: Detailed debugging information, API request/response details
- `INFO`: General operational information, progress updates
- `WARNING`: Warning messages, potential issues
- `ERROR`: Error messages, failed operations
- `CRITICAL`: Critical errors that stop execution

#### `CACHE_DIR`
**Description**: Directory for storing API response cache
**Type**: Path
**Default**: `.cache`

```bash
CACHE_DIR=.cache
```

#### `RESULTS_DIR`
**Description**: Directory for output files (reports, images)
**Type**: Path
**Default**: `results`

```bash
RESULTS_DIR=results
```

#### `FLOW_FILE`
**Description**: Path to the input Flow.json file
**Type**: Path
**Default**: `data/Flow.json`

```bash
FLOW_FILE=data/Flow.json
```

## Configuration Files

### `.env` File Setup

Create a `.env` file in the project root:

```bash
# Required - Your OpenAI API key
OPENAI_API_KEY=sk-proj-your-actual-api-key-here

# Optional - Logging configuration
LOG_LEVEL=INFO

# Optional - Directory configuration
CACHE_DIR=.cache
RESULTS_DIR=results
FLOW_FILE=data/Flow.json
```

### `.env.example` Template

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
LOG_LEVEL=INFO
CACHE_DIR=.cache
RESULTS_DIR=results
FLOW_FILE=data/Flow.json

# Optional: Custom configuration
# MODEL_PREFERENCE=premium  # premium|standard|auto
# MAX_RETRIES=3
# TIMEOUT_SECONDS=60
```

### Security Configuration

#### `.gitignore` Setup
Ensure your `.gitignore` includes:

```gitignore
# Environment variables and API keys
.env
.env.local
.env.production
.env.staging
```

#### API Key Security
- **Never commit** API keys to version control
- Use different keys for development/production
- Rotate keys regularly
- Monitor API usage for unexpected activity

## Environment-Specific Configuration

### Development Environment

```bash
# .env.development
OPENAI_API_KEY=sk-proj-dev-key-here
LOG_LEVEL=DEBUG
CACHE_DIR=.cache/dev
RESULTS_DIR=results/dev
```

### Production Environment

```bash
# .env.production
OPENAI_API_KEY=sk-proj-prod-key-here
LOG_LEVEL=INFO
CACHE_DIR=/app/cache
RESULTS_DIR=/app/results
```

### Testing Environment

```bash
# .env.test
OPENAI_API_KEY=sk-proj-test-key-here
LOG_LEVEL=WARNING
CACHE_DIR=.cache/test
RESULTS_DIR=results/test
```

## Configuration Validation

The application automatically validates configuration on startup:

### Validation Checks
1. **API Key Presence**: Ensures OPENAI_API_KEY is set
2. **Directory Access**: Verifies write permissions for cache and results directories
3. **File Existence**: Checks that the Flow.json file exists and is readable
4. **API Key Validity**: Optional test API call to verify key works

### Validation Errors

#### Missing API Key
```
ERROR: OpenAI API key is required
Solution: Add OPENAI_API_KEY to your .env file
```

#### Invalid Directory
```
ERROR: Cannot create results directory: /invalid/path
Solution: Ensure the parent directory exists and is writable
```

#### Missing Flow File
```
ERROR: Flow file not found: data/Flow.json
Solution: Place your Flow.json file in the specified location
```

## Advanced Configuration

### Custom Configuration Class

For advanced use cases, extend the Config class:

```python
from arcade_flow_analyzer.config import Config
import os

class CustomConfig(Config):
    def __init__(self):
        super().__init__()
        self.CUSTOM_SETTING = os.getenv("CUSTOM_SETTING", "default_value")
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        self.TIMEOUT = int(os.getenv("TIMEOUT_SECONDS", "60"))
```

### Runtime Configuration

Override configuration at runtime:

```python
from arcade_flow_analyzer.config import get_config

config = get_config()
config.LOG_LEVEL = "DEBUG"
config.RESULTS_DIR = Path("custom/results")
config.setup_logging()
```

## Directory Structure Configuration

### Default Structure
```
project/
├── .env                    # Configuration file
├── data/
│   └── Flow.json          # Input data (FLOW_FILE)
├── results/               # Output directory (RESULTS_DIR)
├── .cache/                # Cache directory (CACHE_DIR)
└── logs/                  # Log files
```

### Custom Structure
```bash
# Custom directory configuration
FLOW_FILE=/custom/input/flow-data.json
RESULTS_DIR=/custom/output
CACHE_DIR=/custom/cache
```

## Performance Configuration

### Model Tier Configuration

The analyzer automatically selects model tiers based on complexity, but you can influence this:

```python
# In analyzer.py - customize MODEL_TIERS
MODEL_TIERS = {
    "premium": {
        "model": "gpt-4o",
        "cost_per_1k": 0.03,
        "max_tokens": 4000
    },
    "standard": {
        "model": "gpt-3.5-turbo",
        "cost_per_1k": 0.002,
        "max_tokens": 4000
    }
}
```

### Cache Configuration

Customize caching behavior:

```bash
# Cache configuration
CACHE_DIR=.cache
CACHE_TTL=3600          # Cache time-to-live in seconds
CACHE_MAX_SIZE=1000     # Maximum cache entries
```

## Monitoring Configuration

### Cost Tracking

Monitor API usage:

```python
# Access cost summary after analysis
analyzer = AIAnalyzer()
# ... run analysis ...
cost_summary = analyzer.get_cost_summary()
print(f"Total cost: ${cost_summary['total_cost']:.4f}")
```

### Performance Monitoring

Track performance metrics:

```python
import time
start_time = time.time()
# ... run analysis ...
duration = time.time() - start_time
logger.info(f"Analysis completed in {duration:.2f} seconds")
```

## Troubleshooting Configuration

### Common Issues

#### 1. Environment Not Loading
```bash
# Verify .env file location
ls -la .env

# Check environment variables
python -c "import os; print(os.getenv('OPENAI_API_KEY', 'NOT_SET'))"
```

#### 2. Permission Issues
```bash
# Check directory permissions
ls -la results/ .cache/

# Fix permissions if needed
chmod 755 results/ .cache/
```

#### 3. Path Issues
```bash
# Verify paths are correct
python -c "from pathlib import Path; print(Path('data/Flow.json').exists())"
```

### Debug Configuration

Enable debug mode for configuration troubleshooting:

```python
from arcade_flow_analyzer.config import get_config

config = get_config()
config.display_info()  # Shows all configuration values
```

### Validation Script

Create a configuration validation script:

```python
#!/usr/bin/env python3
"""Configuration validation script."""

from arcade_flow_analyzer.config import get_config
import sys

def validate_config():
    try:
        config = get_config()
        config.validate()
        print("Configuration is valid")
        config.display_info()
        return True
    except Exception as e:
        print(f"Configuration error: {e}")
        return False

if __name__ == "__main__":
    if not validate_config():
        sys.exit(1)
```

## Best Practices

### Security
1. Use separate API keys for different environments
2. Regularly rotate API keys
3. Monitor API usage for unusual activity
4. Never log or expose API keys

### Performance
1. Use appropriate cache directories on fast storage
2. Monitor API costs regularly
3. Adjust log levels based on environment needs
4. Clean cache periodically to free disk space

### Maintenance
1. Document environment-specific configurations
2. Use configuration management tools for production
3. Validate configuration after deployment
4. Keep configuration examples up to date

### Deployment
1. Use environment-specific configuration files
2. Validate configuration before deployment
3. Monitor application startup for configuration errors
4. Have rollback procedures for configuration changes