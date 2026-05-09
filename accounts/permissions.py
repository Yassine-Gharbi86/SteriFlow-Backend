from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admins can access this endpoint."""
    message = 'Admin access required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsAdminOrSelf(BasePermission):
    """Admin can do anything; a regular user can only act on their own record."""
    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_admin:
            return True
        return obj == request.user
