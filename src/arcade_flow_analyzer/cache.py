"""
Cache Management Module

This module contains the CacheManager class responsible for managing
API response caching to optimize costs and performance.
"""

import json
import hashlib
import time
import logging
from pathlib import Path
from typing import Dict, Optional

from .config import get_config

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching of expensive API responses."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the CacheManager.

        Args:
            cache_dir: Optional cache directory path. Uses config default if not provided.
        """
        config = get_config()
        self.cache_dir = cache_dir or config.CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_ttl = config.get_cache_ttl_seconds()

    def _get_cache_key(self, data: str) -> str:
        """
        Generate a cache key from input data.

        Args:
            data: Input data string to generate key from

        Returns:
            MD5 hash of the input data
        """
        return hashlib.md5(data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Dict]:
        """
        Retrieve cached data if it exists and is still valid.

        Args:
            key: Cache key to lookup

        Returns:
            Cached data if available and valid, None otherwise
        """
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)
                    # Check if cache is still valid
                    if time.time() - cached_data["timestamp"] < self.cache_ttl:
                        logger.info(f"Cache hit for key: {key}")
                        return cached_data["data"]
                    else:
                        logger.info(f"Cache expired for key: {key}")
                        cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to load cache for key {key}: {e}")
        return None

    def set(self, key: str, data: Dict) -> None:
        """
        Store data in cache with timestamp.

        Args:
            key: Cache key to store under
            data: Data to cache
        """
        cache_file = self.cache_dir / f"{key}.json"
        cache_data = {"timestamp": time.time(), "data": data}
        try:
            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
            logger.info(f"Cached data for key: {key}")
        except Exception as e:
            logger.warning(f"Failed to cache data for key {key}: {e}")

    def clear(self) -> None:
        """Clear all cached data."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        valid_count = 0
        expired_count = 0

        for cache_file in cache_files:
            try:
                with open(cache_file, "r") as f:
                    cached_data = json.load(f)
                    if time.time() - cached_data["timestamp"] < self.cache_ttl:
                        valid_count += 1
                    else:
                        expired_count += 1
            except Exception:
                expired_count += 1

        return {
            "total_files": len(cache_files),
            "valid_entries": valid_count,
            "expired_entries": expired_count,
        }
