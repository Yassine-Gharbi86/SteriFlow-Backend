from rest_framework.permissions import BasePermission


class IsKitOwnerOrAdmin(BasePermission):
    """
    Object-level permission:
    - Admin can do anything.
    - Regular user can only access their own kits.
    """
    message = 'You do not have permission to access this kit.'

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_admin:
            return True
        return obj.created_by == request.user
