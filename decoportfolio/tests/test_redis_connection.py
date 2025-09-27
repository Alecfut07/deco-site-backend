from django.core.cache import cache
import redis

# Test 1: Check which cache backend is active
print("Cache backend: ", cache.__class__.__name__)

# Test 2: Test Redis connection directly
try:
    r = redis.Redis(host='127.0.0.1', port=6379, db=1)
    r.ping()
    print("Redis connection successful")
except Exception as e:
    print(f"Redis connection failed: {e}")

# Test 3: Test Django cache with Redis
try:
    cache.set('test_key', 'test_value', 60)
    result = cache.get('test_key')
    print(f"Django cache result: {result}")
except Exception as e:
    print(f"Django cache test failed: {e}")

# Test 4: Check if Redis is receiving the data
try:
    r = redis.Redis(host='127.0.0.1', port=6379, db=1)
    keys = r.keys('*')
    print(f"Redis keys: {keys}")
except Exception as e:
    print(f"Redis keys check failed: {e}")