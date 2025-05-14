from rest_framework import permissions

class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Custom permission to check if the user is an admin or superadmin.
    """
    def has_permission(self, request, view):
        # Allow access if the user is a superuser (Admin/SuperAdmin)
        return request.user and (request.user.is_superuser or request.user.is_staff)
