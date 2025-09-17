"""
Configuration management for Arcade Flow Analyzer.

This module centralizes all configuration settings, paths, and environment variables
for better maintainability and organization.
"""

import os
from pathlib import Path
from typing import Optional
import logging

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration class for the application."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    SRC_DIR = PROJECT_ROOT / "src"

    # Data directories
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"

    # Working directories
    CACHE_DIR = PROJECT_ROOT / ".cache"
    RESULTS_DIR = PROJECT_ROOT / "results"
    LOGS_DIR = PROJECT_ROOT / "logs"

    # Input files
    FLOW_FILE = RAW_DATA_DIR / "Flow.json"

    # Output files
    REPORT_FILE = RESULTS_DIR / "flow_analysis_report.md"
    IMAGE_FILE = RESULTS_DIR / "social_media_image.png"
    LOG_FILE = LOGS_DIR / "flow_analysis.log"

    # API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Application settings from environment
    CACHE_TTL_HOURS: int = int(os.getenv("CACHE_TTL_HOURS", "24"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

    @classmethod
    def validate(cls) -> None:
        """Validate configuration and create necessary directories."""
        # Check for required environment variables
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Create necessary directories
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.RAW_DATA_DIR.mkdir(exist_ok=True)
        cls.PROCESSED_DATA_DIR.mkdir(exist_ok=True)
        cls.CACHE_DIR.mkdir(exist_ok=True)
        cls.RESULTS_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)

        # Validate input file exists
        if not cls.FLOW_FILE.exists():
            raise FileNotFoundError(f"Flow file not found: {cls.FLOW_FILE}")

    @classmethod
    def setup_logging(cls) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper()),
            format=cls.LOG_FORMAT,
            handlers=[logging.FileHandler(cls.LOG_FILE), logging.StreamHandler()],
        )

    @classmethod
    def get_cache_ttl_seconds(cls) -> int:
        """Get cache TTL in seconds."""
        return cls.CACHE_TTL_HOURS * 3600

    @classmethod
    def display_info(cls) -> None:
        """Display configuration information for debugging."""
        print("=" * 60)
        print("ARCADE FLOW ANALYZER CONFIGURATION")
        print("=" * 60)
        print(f"Project Root: {cls.PROJECT_ROOT}")
        print(f"Flow File: {cls.FLOW_FILE}")
        print(f"Cache Directory: {cls.CACHE_DIR}")
        print(f"Results Directory: {cls.RESULTS_DIR}")
        print(f"API Key Available: {'Yes' if cls.OPENAI_API_KEY else 'No'}")
        print(f"Cache TTL: {cls.CACHE_TTL_HOURS} hours")
        print("=" * 60)


# Create global config instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


# Convenience functions for common paths
def get_flow_file_path() -> Path:
    """Get the path to the flow data file."""
    return config.FLOW_FILE


def get_cache_dir() -> Path:
    """Get the cache directory path."""
    return config.CACHE_DIR


def get_results_dir() -> Path:
    """Get the results directory path."""
    return config.RESULTS_DIR


def get_openai_api_key() -> str:
    """Get the OpenAI API key, raising an error if not set."""
    if not config.OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured")
    return config.OPENAI_API_KEY
