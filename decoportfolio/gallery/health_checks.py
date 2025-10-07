import redis
import time
from django.core.cache import cache
from django.conf import settings

class CacheHealthCheck:
    """Cache health monitoring system"""

    @staticmethod
    def check_redis_connection():
        """Check if Redis is accessible"""
        try:
            r = redis.Redis(host='127.0.0.1', port=6379, db=1)
            r.ping()
            return True, "Redis connection OK"
        except Exception as e:
            return False, f"Redis connection failed: {e}"

    