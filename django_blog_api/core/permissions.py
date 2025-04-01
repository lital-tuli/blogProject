# django_blog_api/core/permissions.py
from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Allow read access to all users, but only write access to admin users or editors.
    
    Admin users are defined as either:
    1. Users with is_staff=True
    2. Users belonging to the 'management' or 'editors' groups
    """
    def has_permission(self, request, view):
        # Allow read-only methods for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow write access if user is authenticated and is admin/editor
        if request.user.is_authenticated:
            # Check if user is staff or belongs to the right groups
            return (request.user.is_staff or 
                    request.user.groups.filter(name__in=['editors', 'management']).exists())
        return False
    
    def has_object_permission(self, request, view, obj):
        # Allow read-only methods for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow write access if user is authenticated and is admin/editor
        if request.user.is_authenticated:
            # Check if user is staff or belongs to the right groups
            return (request.user.is_staff or 
                    request.user.groups.filter(name__in=['editors', 'management']).exists())
        return False

class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """
    Allow read access to all users, but write access only to the author or admin users.
    For delete operations, only allow admins or the author.
    
    This is useful for models with an 'author' field like articles or comments.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read access for all
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # For delete operations, allow if admin/management or the author
        if request.method == 'DELETE':
            return (request.user.is_staff or 
                    request.user.groups.filter(name='management').exists() or
                    obj.author == request.user)
        
        # For update operations, allow author or admins/editors/management
        return (obj.author == request.user or 
                request.user.is_staff or 
                request.user.groups.filter(name__in=['editors', 'management']).exists())
    
    def has_permission(self, request, view):
        # Allow read access for all
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For write operations, require authentication
        return request.user and request.user.is_authenticated

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `author` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the author
        return obj.author == request.user