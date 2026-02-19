from django.core.cache import cache
import redis

def debug_cache():
    print("=== CACHE DEBUG ===")

    # Test 1: Cache backend
    print(f"Cache backend: {cache.__class__.__name__}")

    # Test 2: Direct Redis test
    try:
        r = redis.Redis(host='127.0.0.1', port=6379, db=1)
        r.ping()
        print("Redis connection: OK")
    except Exception as e:
        print(f"Redis connection: {e}")
    
    # Test 3: Django cache test
    try:
        cache.set('debug_test', 'hello_world', 60)
        result = cache.get('debug_test')
        print(f"Django cache: {result}")
    except Exception as e:
        print(f"Django cache: {e}")
    
    # Test 4: Check Redis keys
    try:
        r = redis.Redis(host='127.0.0.1', port=6379, db=1)
        keys = r.keys('*')
        print(f"Redis keys found: {len(keys)}")
        for key in keys:
            print(f"  - {key}")
    except Exception as e:
        print(f"Redis keys: {e}")
    
if __name__ == "__main__":
    debug_cache()