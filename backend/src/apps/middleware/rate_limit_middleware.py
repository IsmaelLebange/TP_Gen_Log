from django.http import HttpResponseTooManyRequests
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}

    def __call__(self, request):
        # Simple rate limiting logic
        ip = request.META.get('REMOTE_ADDR')
        now = time.time()
        if ip in self.requests and now - self.requests[ip] < 1:  # 1 request per second
            return HttpResponseTooManyRequests("Rate limit exceeded")
        self.requests[ip] = now
        return self.get_response(request)