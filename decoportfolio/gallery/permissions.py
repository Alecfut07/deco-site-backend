from rest_framework.permissions import BasePermission

class IsFamilyMember(BasePermission):
    """
    Allow access only to users who belong to the 'Family' group (or are superusers).
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.groups.filter(name="Family").exists()