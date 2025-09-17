"""
Unit tests for the CacheManager module.
"""

import json
import time
import pytest
from unittest.mock import patch, Mock
from arcade_flow_analyzer.cache import CacheManager


class TestCacheManager:
    """Test cases for the CacheManager class."""

    def test_init(self, temp_cache_dir):
        """Test CacheManager initialization."""
        cache_manager = CacheManager(temp_cache_dir)

        assert cache_manager.cache_dir == temp_cache_dir
        assert temp_cache_dir.exists()

    def test_init_with_config(self, mock_config):
        """Test CacheManager initialization using config."""
        with patch("arcade_flow_analyzer.cache.get_config", return_value=mock_config):
            cache_manager = CacheManager()
            assert cache_manager.cache_dir == mock_config.CACHE_DIR

    def test_get_cache_key(self, temp_cache_dir):
        """Test cache key generation."""
        cache_manager = CacheManager(temp_cache_dir)
        key = cache_manager._get_cache_key("test data")

        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length
        assert key == cache_manager._get_cache_key("test data")  # Consistent

    def test_set_and_get_cache(self, temp_cache_dir):
        """Test setting and getting cache data."""
        cache_manager = CacheManager(temp_cache_dir)
        test_data = {"test": "data", "number": 123}
        test_key = "test_key"

        # Set cache
        cache_manager.set(test_key, test_data)

        # Verify cache file exists
        cache_file = temp_cache_dir / f"{test_key}.json"
        assert cache_file.exists()

        # Get cache
        retrieved_data = cache_manager.get(test_key)
        assert retrieved_data == test_data

    def test_get_nonexistent_cache(self, temp_cache_dir):
        """Test getting cache data that doesn't exist."""
        cache_manager = CacheManager(temp_cache_dir)
        result = cache_manager.get("nonexistent_key")

        assert result is None

    def test_cache_expiration(self, temp_cache_dir):
        """Test cache expiration functionality."""
        # Mock a very short TTL
        with patch("arcade_flow_analyzer.cache.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.CACHE_DIR = temp_cache_dir
            mock_config.get_cache_ttl_seconds.return_value = 1  # 1 second TTL
            mock_get_config.return_value = mock_config

            cache_manager = CacheManager(temp_cache_dir)
            test_data = {"test": "data"}
            test_key = "expiring_key"

            # Set cache
            cache_manager.set(test_key, test_data)

            # Should be available immediately
            assert cache_manager.get(test_key) == test_data

            # Wait for expiration
            time.sleep(1.1)

            # Should be expired now
            assert cache_manager.get(test_key) is None

    def test_cache_file_corruption(self, temp_cache_dir):
        """Test handling of corrupted cache files."""
        cache_manager = CacheManager(temp_cache_dir)
        test_key = "corrupted_key"

        # Create corrupted cache file
        cache_file = temp_cache_dir / f"{test_key}.json"
        cache_file.write_text("invalid json content")

        # Should handle corruption gracefully
        result = cache_manager.get(test_key)
        assert result is None

    def test_clear_cache(self, temp_cache_dir):
        """Test clearing all cache data."""
        cache_manager = CacheManager(temp_cache_dir)

        # Set multiple cache entries
        cache_manager.set("key1", {"data": 1})
        cache_manager.set("key2", {"data": 2})

        # Verify files exist
        assert len(list(temp_cache_dir.glob("*.json"))) == 2

        # Clear cache
        cache_manager.clear()

        # Verify files are gone
        assert len(list(temp_cache_dir.glob("*.json"))) == 0

    def test_get_cache_stats(self, temp_cache_dir):
        """Test cache statistics generation."""
        with patch("arcade_flow_analyzer.cache.get_config") as mock_get_config:
            mock_config = Mock()
            mock_config.CACHE_DIR = temp_cache_dir
            mock_config.get_cache_ttl_seconds.return_value = 3600  # 1 hour TTL
            mock_get_config.return_value = mock_config

            cache_manager = CacheManager(temp_cache_dir)

            # Set some cache entries
            cache_manager.set("valid1", {"data": 1})
            cache_manager.set("valid2", {"data": 2})

            # Create an expired entry manually
            expired_cache = {
                "timestamp": time.time() - 7200,  # 2 hours ago
                "data": {"data": "expired"},
            }
            expired_file = temp_cache_dir / "expired.json"
            with open(expired_file, "w") as f:
                json.dump(expired_cache, f)

            stats = cache_manager.get_cache_stats()

            assert stats["total_files"] == 3
            assert stats["valid_entries"] == 2
            assert stats["expired_entries"] == 1

    def test_set_cache_write_error(self, temp_cache_dir):
        """Test handling of cache write errors."""
        cache_manager = CacheManager(temp_cache_dir)

        # Make cache directory read-only to cause write error
        temp_cache_dir.chmod(0o444)

        # Should handle write error gracefully
        try:
            cache_manager.set("test_key", {"data": "test"})
            # Should not raise an exception
        finally:
            # Restore permissions for cleanup
            temp_cache_dir.chmod(0o755)
