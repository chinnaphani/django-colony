from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsAssociationActive(BasePermission):
    """
    Allows access only if the user's association is active.
    """
    def has_permission(self, request, view):
        if hasattr(request.user, 'association') and request.user.association:
            if request.user.association.active:
                return True
            raise PermissionDenied(detail="Your association is inactive.")
        raise PermissionDenied(detail="No association found for the user.")
