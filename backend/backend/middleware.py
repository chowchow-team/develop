from django.core.cache import cache
from django.http import HttpResponseForbidden
import time

class IPAnalyzerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        
        if self.is_ip_blacklisted(ip):
            return HttpResponseForbidden("Access Denied")

        self.log_request(ip)
        
        if self.is_ip_suspicious(ip):
            self.add_to_blacklist(ip)
            return HttpResponseForbidden("Access Denied due to suspicious activity")

        return self.get_response(request)

    def is_ip_blacklisted(self, ip):
        return cache.get(f"blacklist_{ip}")

    def log_request(self, ip):
        current_time = time.time()
        requests = cache.get(f"requests_{ip}", [])
        requests.append(current_time)

        requests = [r for r in requests if current_time - r <= 300]
        cache.set(f"requests_{ip}", requests, timeout=300)

    def is_ip_suspicious(self, ip):
        requests = cache.get(f"requests_{ip}", [])
        if len(requests) > 500:
            return True
        
        endpoint_counts = cache.get(f"endpoint_counts_{ip}", {})
        if any(count > 500 for count in endpoint_counts.values()):
            return True

        return False

    def add_to_blacklist(self, ip):
        cache.set(f"blacklist_{ip}", True, timeout=3600)