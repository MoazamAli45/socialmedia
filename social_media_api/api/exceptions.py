from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied
from django.db import IntegrityError
from django.http import Http404
import logging

logger = logging.getLogger('api')

def custom_exception_handler(exc, context):
    """
    Custom exception handler for all API routes, returning a standardized error response.
    """
    # Get the default DRF response
    response = exception_handler(exc, context)
    
    # Standardized error response structure
    error_response = {
        'error': {
            'code': 'unknown_error',
            'message': 'An unexpected error occurred',
            'details': {}
        }
    }
    
    # Handle specific exceptions
    if isinstance(exc, ValidationError):
        error_response['error']['code'] = 'validation_error'
        error_response['error']['message'] = 'Invalid input data'
        error_response['error']['details'] = exc.detail
        status_code = 400
    elif isinstance(exc, AuthenticationFailed):
        error_response['error']['code'] = 'authentication_failed'
        error_response['error']['message'] = 'Invalid or missing authentication credentials'
        error_response['error']['details'] = {'detail': str(exc)}
        status_code = 401
    elif isinstance(exc, PermissionDenied):
        error_response['error']['code'] = 'permission_denied'
        error_response['error']['message'] = 'You do not have permission to perform this action'
        error_response['error']['details'] = {'detail': str(exc)}
        status_code = 403
    elif isinstance(exc, Http404):
        error_response['error']['code'] = 'not_found'
        error_response['error']['message'] = 'Resource not found'
        error_response['error']['details'] = {'detail': str(exc)}
        status_code = 404
    elif isinstance(exc, IntegrityError):
        error_response['error']['code'] = 'database_error'
        error_response['error']['message'] = 'Database integrity error'
        error_response['error']['details'] = {'error': str(exc)}
        status_code = 400
    else:
        error_response['error']['code'] = getattr(exc, 'default_code', 'server_error')
        error_response['error']['message'] = 'Internal server error'
        error_response['error']['details'] = {'error': str(exc)} if not response else response.data
        status_code = 500
    
    # Log the error
    view_name = context['view'].__class__.__name__ if 'view' in context else 'Unknown'
    logger.error(f"Exception in {view_name}: {str(exc)}")
    
    # Return response
    from rest_framework.response import Response
    return Response(error_response, status=status_code)