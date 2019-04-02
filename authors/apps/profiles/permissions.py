from rest_framework.permissions import BasePermission
from .models import Record


class Owner(BasePermission):
    """Class checks and confirms the owneership of record before any alteration"""

    def has_object_permission(self, request, view, obj):
        """Return true in the case permission has been granted to the editor"""
        if isinstance(obj, Record):
            return obj.owner == request.user