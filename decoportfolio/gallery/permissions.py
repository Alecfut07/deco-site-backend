from rest_framework.permissions import BasePermission
from gallery.models import FamilyMember


class IsFamilyMember(BasePermission):
    """
    Allow access only to authenticated FamilyMembers users.
    This is completely separate from Django Admin users.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # Check if user is a FamilyMember instance
        return isinstance(user, FamilyMember) and user.is_active
