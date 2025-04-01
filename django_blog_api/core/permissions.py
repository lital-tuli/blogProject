from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Allow read access to all users, but only write access to admin users or editors.
    """
    def has_permission(self, request, view):
        # Allow read-only methods for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow write access if user is in editors or management group
        if request.user.is_authenticated:
            return (request.user.is_staff or 
                    request.user.groups.filter(name__in=['editors', 'management']).exists())
        return False

class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """
    Allow read access to all users, but write access only to the author or admin users.
    For delete operations, only allow admins.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read access for all
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For delete operations, only allow admins or management
        if request.method == 'DELETE':
            return (request.user.is_staff or 
                    request.user.groups.filter(name='management').exists())
        
        # For update operations, allow author or admins/editors/management
        return (obj.author == request.user or 
                request.user.is_staff or 
                request.user.groups.filter(name__in=['editors', 'management']).exists())