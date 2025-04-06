from rest_framework import permissions

class EditorOrAdminPermissionMixin:
    """
    Mixin to check if user is editor or admin.
    """
    def is_editor_or_admin(self, user):
        return (
            user.is_authenticated and 
            (user.is_staff or user.groups.filter(name__in=['editors', 'management']).exists())
        )
        
    def is_admin(self, user):
        return (
            user.is_authenticated and 
            (user.is_staff or user.groups.filter(name='management').exists())
        )

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff) 
    
class IsAdminUserOrReadOnly(permissions.BasePermission, EditorOrAdminPermissionMixin):
    """Allow read access to all users, but only write access to admin users or editors."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.is_editor_or_admin(request.user)
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.is_editor_or_admin(request.user)

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
    
    class EditorOrAdminPermissionMixin:
        """
        Mixin to check if user is editor or admin.
        """
        def is_editor_or_admin(self, user):
            return (
                user.is_authenticated and 
                (user.is_staff or user.groups.filter(name__in=['editors', 'management']).exists())
            )
            
        def is_admin(self, user):
            return (
                user.is_authenticated and 
                (user.is_staff or user.groups.filter(name='management').exists())
            )