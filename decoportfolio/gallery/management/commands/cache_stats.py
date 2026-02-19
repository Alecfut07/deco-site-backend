import redis
import time
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings

class Command(BaseCommand):
    help = 'Display cache statistics and performance metrics'

    def handle(self, *args, **options):
        self.stdout.write("CACHE STATISTICS REPORT")
        self.stdout.write("=" * 50)

        # Redis connection
        try:
            r = redis.Redis(host='127.0.0.1', port=6379, db=1)
            r.ping()

            # Memory usage
            memory_usage = r.info('memory')
            self.stdout.write(f"Memory Usage: {memory_usage['used_memory_human']}")
            self.stdout.write(f"Peak Memory: {memory_usage['used_memory_peak_human']}")


            # Key statistics
            keys = r.keys('decoportfolio:1:*')
            self.stdout.write(f"Total Cache Keys: {len(keys)}")

            # Cache key breakdown
            key_types = {}
            for key in keys:
                key_str = key.decode('utf-8')
                if 'portfolio_list' in key_str:
                    key_types['Portfolio Lists'] = key_types.get('Portfolio Lists', 0) + 1
                elif 'portfolio_item' in key_str:
                    key_types['Portfolio Items'] = key_types.get('Portfolio Items', 0) + 1
                elif 'category' in key_str:
                    key_types['Categories'] = key_types.get('Categories', 0) + 1
                elif 'service' in key_str:
                    key_types['Services'] = key_types.get('Services', 0) + 1
                elif 'business_info' in key_str:
                    key_types['Business Info'] = key_types.get('Business Info', 0) + 1
                else:
                    key_types['Other'] = key_types.get('Other', 0) + 1
            
            self.stdout.write("\nCache Key Breakdown:")
            for key_type, count in key_types.items():
                self.stdout.write(f"  {key_type}: {count}")
            
            # Performance test
            self.stdout.write("\nPerformance Test:")
            start_time = time.time()
            test_key = 'performance_test'
            cache.set(test_key, {'test': 'data'}, 60)
            cache.get(test_key)
            cache.delete(test_key)
            end_time = time.time()

            self.stdout.write(f"  Cache operations: {(end_time - start_time) * 1000:.2f}ms")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Redis connection failed: {e}"))

        self.stdout.write("\nCache statistics report completed!")