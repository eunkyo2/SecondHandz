class SecurityHeadersMiddleware:
    """Content-Security-Policy 헤더 부여 (X-Frame-Options/X-Content-Type-Options는 Django 기본값으로 이미 처리됨)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; connect-src 'self' ws: wss:"
        )
        return response
