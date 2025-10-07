from django.core.management.base import BaseCommand
from gallery.health_checks import CacheHealthCheck

class Command(BaseCommand):
    help = 'Run cache health checks'
    
    def handle(self, *args, **options):
        self.stdout.write("CACHE HEALTH CHECK")
        self.stdout.write("=" * 30)

        health_status = CacheHealthCheck.get_health_status()

        for check_name, result in health_status['details'].items():
            if isinstance(result, tuple):
                status, message = result
                if status:
                    self.stdout.write(self.style.SUCCESS(f"SUCCESS = {check_name}: {message}"))
                else:
                    self.stdout.write(self.style.ERROR(f"ERROR = {check_name}: {message}"))
        
        if health_status['healthy']:
            self.stdout.write(self.style.SUCCESS("\nAll cache health checks passed!"))
        else:
            self.stdout.write(self.style.ERROR("\nSome cache health checks failed!"))