import json
import gzip
import base64
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