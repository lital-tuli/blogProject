from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound, ValidationError, PermissionDenied
from rest_framework.views import exception_handler
import logging
import traceback
import json

# Set up logging
logger = logging.getLogger(__name__)

def error_response(message, status_code=status.HTTP_400_BAD_REQUEST, errors=None, error_code=None):
    """
    Standardized error response format for the API.
    
    Args:
        message (str): The main error message
        status_code (int): HTTP status code
        errors (dict, optional): Detailed error information, typically from serializer errors
        error_code (str, optional): A specific error code for client-side handling
    
    Returns:
        Response: A DRF Response object with consistent error format
    """
    data = {
        "success": False,
        "message": message
    }
    
    if error_code:
        data["error_code"] = error_code
        
    if errors:
        data["errors"] = errors
        
    return Response(data, status=status_code)

def success_response(data=None, message=None, status_code=status.HTTP_200_OK):
    """
    Standardized success response format for the API.
    
    Args:
        data (any, optional): The response data
        message (str, optional): A success message
        status_code (int): HTTP status code
    
    Returns:
        Response: A DRF Response object with consistent success format
    """
    response_data = {
        "success": True,
    }
    
    if message:
        response_data["message"] = message
        
    if data is not None:
        response_data["data"] = data
        
    return Response(response_data, status=status_code)

def custom_exception_handler(exc, context):
    """
    Custom exception handler for standardized error responses.
    
    This handler takes the standard DRF exception handler response and
    reformats it to match our standardized error response format.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    # Get request details for logging
    request = context.get("request", None)
    method = getattr(request, "method", "")
    path = getattr(request, "path", "")
    user_id = getattr(request.user, "id", "Anonymous") if request else "Unknown"
    
    # Log the error with trace
    if response is not None:
        logger.error(
            f"API Error: {exc}, Status: {response.status_code}, "
            f"User: {user_id}, Method: {method}, Path: {path}\n"
            f"Traceback: {traceback.format_exc()}"
        )
    else:
        logger.error(
            f"Unhandled Exception: {exc}, "
            f"User: {user_id}, Method: {method}, Path: {path}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        # If it's not an API exception, it's likely a server error
        return Response(
            {
                "success": False,
                "message": "An internal server error occurred.",
                "error_code": "server_error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Format the response to match our error_response format
    if isinstance(exc, ValidationError):
        # Validation errors have a different format
        return Response(
            {
                "success": False,
                "message": "Validation error",
                "errors": exc.detail,
                "error_code": "validation_error"
            },
            status=response.status_code
        )
    elif isinstance(exc, NotFound):
        return Response(
            {
                "success": False,
                "message": str(exc),
                "error_code": "not_found"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    elif isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "message": "You do not have permission to perform this action.",
                "error_code": "permission_denied"
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    # For other exceptions, format the response consistently
    if hasattr(response, 'data'):
        if isinstance(response.data, dict) and 'detail' in response.data:
            message = response.data['detail']
        else:
            message = str(exc)
            
        return Response(
            {
                "success": False,
                "message": message,
                "error_code": f"error_{response.status_code}"
            },
            status=response.status_code
        )
    
    return response