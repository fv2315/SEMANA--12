import logging
import uuid


logger = logging.getLogger('core.security')


class RequestAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = uuid.uuid4().hex
        request.request_id = request_id

        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Content-Security-Policy'] = (
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; frame-ancestors 'none'"
        )

        logger.info(
            'request_id=%s method=%s path=%s status=%s',
            request_id,
            request.method,
            request.path,
            response.status_code,
        )
        return response
