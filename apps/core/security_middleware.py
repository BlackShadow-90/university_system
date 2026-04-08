"""
Security middleware for rate limiting and additional protections
"""
import time
from django.http import JsonResponse, HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings


class RateLimitMiddleware:
    """
    Middleware to implement rate limiting for sensitive endpoints
    """
    
    # Rate limits: (requests, window_seconds)
    RATE_LIMITS = {
        'login': (5, 300),  # 5 attempts per 5 minutes
        'password_reset': (3, 3600),  # 3 attempts per hour
        'api': (100, 60),  # 100 requests per minute for API
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip rate limiting for exempt paths
        if self._is_exempt(request):
            return self.get_response(request)
        
        # Check rate limit
        rate_limit_key = self._get_rate_limit_key(request)
        if rate_limit_key:
            is_allowed, remaining = self._check_rate_limit(request, rate_limit_key)
            if not is_allowed:
                return self._get_rate_limit_response()
        
        response = self.get_response(request)
        
        # Add rate limit headers if applicable
        if rate_limit_key and 'remaining' in locals():
            response['X-RateLimit-Remaining'] = remaining
        
        return response
    
    def _is_exempt(self, request):
        """Check if request should be exempt from rate limiting"""
        # Exempt static and media files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return True
        
        # Exempt admin for staff users
        if request.path.startswith('/admin/') and request.user.is_staff:
            return True
        
        return False
    
    def _get_rate_limit_key(self, request):
        """Determine which rate limit applies to this request"""
        path = request.path.lower()
        
        if 'login' in path or 'auth' in path:
            return 'login'
        elif 'password' in path and 'reset' in path:
            return 'password_reset'
        elif path.startswith('/api/'):
            return 'api'
        
        return None
    
    def _check_rate_limit(self, request, limit_type):
        """Check if request is within rate limit"""
        if limit_type not in self.RATE_LIMITS:
            return True, None
        
        max_requests, window = self.RATE_LIMITS[limit_type]
        
        # Create cache key based on IP and limit type
        ip = self._get_client_ip(request)
        cache_key = f"ratelimit:{limit_type}:{ip}"
        
        # Get current count
        current = cache.get(cache_key, 0)
        
        if current >= max_requests:
            return False, 0
        
        # Increment counter
        cache.set(cache_key, current + 1, window)
        
        return True, max_requests - current - 1
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
    
    def _get_rate_limit_response(self):
        """Return response when rate limit is exceeded"""
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.',
                'retry_after': 300
            }, status=429)
        
        return HttpResponseForbidden(
            "Too many requests. Please try again later.",
            content_type="text/plain"
        )


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy (CSP)
        csp = "default-src 'self'; "
        csp += "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        csp += "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
        csp += "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
        csp += "img-src 'self' data: https:; "
        csp += "connect-src 'self';"
        response['Content-Security-Policy'] = csp
        
        return response


class AuditLogMiddleware:
    """
    Middleware to log sensitive actions for audit purposes
    """
    
    SENSITIVE_PATHS = [
        '/auth/login/',
        '/auth/logout/',
        '/auth/password/',
        '/admin/',
        '/api/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log sensitive requests before processing
        if self._is_sensitive(request):
            self._log_request(request)
        
        response = self.get_response(request)
        
        # Log response for sensitive requests
        if self._is_sensitive(request):
            self._log_response(request, response)
        
        return response
    
    def _is_sensitive(self, request):
        """Check if request path is sensitive"""
        path = request.path.lower()
        return any(sensitive in path for sensitive in self.SENSITIVE_PATHS)
    
    def _log_request(self, request):
        """Log the request details"""
        import logging
        logger = logging.getLogger('audit')
        
        logger.info(
            f"Request: {request.method} {request.path} | "
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'} | "
            f"IP: {self._get_client_ip(request)}"
        )
    
    def _log_response(self, request, response):
        """Log the response details"""
        import logging
        logger = logging.getLogger('audit')
        
        logger.info(
            f"Response: {response.status_code} | "
            f"Path: {request.path} | "
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'}"
        )
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
