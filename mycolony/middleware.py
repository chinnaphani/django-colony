import logging

logger = logging.getLogger(__name__)

class SessionDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log session info before processing
        if hasattr(request, 'session'):
            logger.info(f"Session ID: {request.session.session_key}")
            logger.info(f"User: {getattr(request, 'user', 'Anonymous')}")
            logger.info(f"Authenticated: {request.user.is_authenticated}")
        
        response = self.get_response(request)
        
        # Log session info after processing
        if hasattr(request, 'session') and request.session.modified:
            logger.info(f"Session modified: {request.session.session_key}")
        
        return response 