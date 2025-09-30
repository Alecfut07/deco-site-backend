import json
import gzip
import base64
import time
import hashlib
from django.core.cache import cache
from django.conf import settings

class AdvancedCache:
    """Advanced caching with versioning and compression"""

    CACHE_VERSION = 1
    COMPRESSION_THRESHOLD = 1024 # Compress data larger than 1KB

    @classmethod
    def _compress_data(cls, data):
        """Compress data if it's large enough"""
        json_data = json.dumps(data)
        if len(json_data) > cls.COMPRESSION_THRESHOLD:
            compressed = gzip.compress(json_data.encode('utf-8'))
            return base64.b64encode(compressed).decode('utf-8'), True
        return json_data, False
    
    @classmethod
    def _decompress_data(cls, data, is_compressed):
        """Decompress data if it was compressed"""
        if is_compressed:
            compressed_data = base64.b64decode(data.encode('utf-8'))
            json_data = gzip.decompress(compressed_data).decode('utf-8')
            return json.loads(json_data)
        return json.loads(data)

    @classmethod
    def set(cls, key, data, timeout=300, version=None):
        """Set cache with compression and versioning"""
        version = version or cls.CACHE_VERSION
        versioned_key = f"{key}:v{version}"

        # Compress data if needed
        compressed_data, is_compressed = cls._compress_data(data)

        cache_data = {
            'data': compressed_data,
            'compressed': is_compressed,
            'version': version,
            'timestamp': time.time()
        }

        cache.set(versioned_key, cache_data, timeout)
        print(f"Cached {key} (compressed: {is_compressed}, version: {version})")

    @classmethod
    def get(cls, key, version=None):
        """Get cache with decompression and versioning"""
        version = version or cls.CACHE_VERSION
        versioned_key = f"{key}:v{version}"

        cache_data = cache.get(versioned_key)
        if cache_data:
            try:
                data = cls._decompress_data(
                    cache_data['data'],
                    cache_data.get('compressed', False)
                )
                print(f"Cache hit: {key} (version: {version})")
                return data
            except Exception as e:
                print(f"Cache decompression error: {e}")
                cache.delete(versioned_key)

        print(f"Cache miss: {key}")
        return None

    @classmethod
    def delete(cls, key, version=None):
        """Delete cache with versioning"""
        version = version or cls.CACHE_VERSION
        versioned_key = f"{key}:v{version}"
        cache.delete(versioned_key)
        print(f"Deleted cache: {key} (version: {version})")

    