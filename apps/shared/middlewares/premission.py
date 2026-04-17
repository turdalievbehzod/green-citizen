import logging 
import re

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.users.models.permissions import Endpoint

logger = logging.getLogger('permissions')


class EndpointPermissionMiddleware(MiddlewareMixin):    
    """ 
    Middleware to check if the user has permission to access the 
    endpoint based on their roles and permissions.
    """
    SKIP_PREFIXES = [
        '/admin/',
        '/static/,',
        '/media/',
        '/schema/',
        '/api/v1/docs/',
        '/api/v1/redoc/',
        '/api/v1/users/login/'
    ]
    
    def process_request(self, request):
        # Skip for non-API endpoints
        if not request.path.startswith('/api/'):
            return None
    
        # Skip for media, static, admin, schema, docs
        for prefix in self.SKIP_PREFIXES:
            if request.path.startswith(prefix):
                return None
            
        #  Try to authenticate the user
        jwt_authenticator = JWTAuthentication()
        try:
            auth_result = jwt_authenticator.authenticate(request)
            if auth_result is not None:
                request.user, request.auth = auth_result
        except Exception as e:
            logger.debug(f"Authentication failed: {str(e)}")
            return None
        if auth_result is None:
            logger.debug("No authentication credentials provided.") 
            return None
        # Normalize the path (replace IDs with {id})
        normalized_path = self.normalize_path(request.path)
        
        # Check access from database (this now handles all access types)
        has_access = Endpoint.check_access(
            user = request.user if  hasattr(request, 'user') else None,
            path = normalized_path, 
            method = request.method
        )
        
        if not has_access:
            # Get endpoint to show better error message
            endpoint = Endpoint.objects.filter(
                path = normalized_path, 
                method = request.method.upper(),
                is_active = True
            ).first()
            
            if endpoint:
                if endpoint.access_type == 'public':
                    error_detail = f'This endpoint is temporarily unavailable.'
                elif endpoint.access_type == 'authenticated':
                    error_detail = f'Authentication required to access {request.method} {request.path}'
                else: #permission
                    error_detail = f'You do not have permission to access {request.method} {request.path}'
            else:
                error_detail = f'Endpoint not found or not configured: {request.method} {request.path}'
            
            logger.warning(
                f"Access denied for user {getattr(request.user, 'username', 'Anonymous')}"
                f"tried to access {request.method} {request.path}"
            )
            
            return JsonResponse(
                {
                    'error': 'Access Denied',
                    'detail': error_detail
                },
                status=403 if hasattr(request, 'user') and request.user.is_authenticated else 401
            )
            
        @staticmethod
        def normalize_path(path):
            """ 
            Normalize path with clear slug detection
            """
            
            STATIC_SEGMENTS = {'api', 'v1', 'v2', 'user-profiles', 'order-items' }
            
            parts = path.split('/')
            normalized_parts = []
            
            for part in parts:
                # Empty parts known static segments
                if not part or part in STATIC_SEGMENTS:
                    normalized_parts.append(part)
                # Dynamic segments (IDs/slugs)
                elif (part.isdigit() or
                      part.startswith('slug-') or
                      re.match(r'^[0-9a-f-]{32,}$', part)): #UUID-like
                    normalized_parts.append('{id}')
                # Everything else stays as-is
                else:
                    normalized_parts.append(part)
                    
            return '/'.join(normalized_parts)