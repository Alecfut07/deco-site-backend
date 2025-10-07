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

    @staticmethod
    def check_cache_performance():
        """Check cache read/write performance"""
        try:
            test_key = 'health_check_test'
            test_data = {'timestamp': time.time(), 'test': 'data'}

            # Test write
            start_time = time.time()
            cache.set(test_key, test_data, 60)
            write_time = (time.time() - start_time) * 1000

            # Test read
            start_time = time.time()
            result = cache.get(test_key)
            read_time = (time.time() - start_time) * 1000

            # Cleanup
            cache.delete(test_key)

            if result and result.get('test'):
                return True, f"Cache performance OK (write: {write_time:.2f}ms, read: {read_time:.2f}ms)"
            else:
                return False, "Cache read/write test failed"
            
        except Exception as e:
            return False, f"Cache performance test failed: {e}"