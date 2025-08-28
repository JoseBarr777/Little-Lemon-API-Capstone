from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsManagerOrReadOnly(BasePermission):
    """Read for authenticated users. Writes only for users in the 'Manager' group."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.groups.filter(name="Manager").exists()

class IsManager(BasePermission):
    """Only users in the 'Manager' group or superusers can access."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.groups.filter(name='Manager').exists() or request.user.is_superuser)
        )

class IsCustomer(BasePermission):
    """Only authenticated users who are NOT in Manager or Delivery Crew groups."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superusers can access (for testing)
        if request.user.is_superuser:
            return True
            
        # Users not in any special groups are customers
        return not (
            request.user.groups.filter(name__in=['Manager', 'Delivery Crew']).exists()
        )

class IsDeliveryCrew(BasePermission):
    """Only users in the 'Delivery Crew' group or superusers can access."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.groups.filter(name='Delivery Crew').exists() or request.user.is_superuser)
        )
