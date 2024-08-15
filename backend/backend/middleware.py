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
        # 최근 5분 동안의 요청만 유지
        requests = [r for r in requests if current_time - r <= 300]
        cache.set(f"requests_{ip}", requests, timeout=300)

    def is_ip_suspicious(self, ip):
        requests = cache.get(f"requests_{ip}", [])
        # 5분 동안 100회 이상의 요청을 의심스러운 활동으로 정의
        if len(requests) > 100:
            return True
        
        # 특정 엔드포인트에 대한 과도한 요청을 의심스러운 활동으로 정의
        endpoint_counts = cache.get(f"endpoint_counts_{ip}", {})
        if any(count > 50 for count in endpoint_counts.values()):
            return True

        return False

    def add_to_blacklist(self, ip):
        cache.set(f"blacklist_{ip}", True, timeout=3600)  # 1시간 동안 블랙리스트에 추가