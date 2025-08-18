from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsManagerOrReadOnly(BasePermission):
    """Read for everyone. Writes only for users in the 'Manager' group."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        return u.is_authenticated and u.groups.filter(name="Manager").exists()
