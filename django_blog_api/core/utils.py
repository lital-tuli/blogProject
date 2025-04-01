from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound, ValidationError, PermissionDenied
from rest_framework.views import exception_handler
import logging

# Set up logging
logger = logging.getLogger(__name__)

def error_response(message, status_code=status.HTTP_400_BAD_REQUEST, errors=None):
    """
    Standardized error response format for the API.
    
    Args:
        message (str): The main error message
        status_code (int): HTTP status code
        errors (dict, optional): Detailed error information, typically from serializer errors
    
    Returns:
        Response: A DRF Response object with consistent error format
    """
    data = {"detail": message}
    
    if errors:
        data["errors"] = errors
        
    return Response(data, status=status_code)

def custom_exception_handler(exc, context):
    """
    Custom exception handler for standardized error responses.
    
    This handler takes the standard DRF exception handler response and
    reformats it to match our standardized error response format.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the error
    if response is not None:
        logger.error(f"API Error: {exc}, Status: {response.status_code}")
    else:
        logger.error(f"Unhandled Exception: {exc}")
        # If it's not an API exception, it's likely a server error
        return Response(
            {"detail": "An internal server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Format the response to match our error_response format
    if isinstance(exc, ValidationError):
        # Validation errors have a different format
        return Response(
            {"detail": "Validation error", "errors": exc.detail},
            status=response.status_code
        )
    elif isinstance(exc, NotFound):
        return Response(
            {"detail": str(exc)},
            status=status.HTTP_404_NOT_FOUND
        )
    elif isinstance(exc, PermissionDenied):
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # For other exceptions, use the response as is
    return response