from rest_framework import permissions


# Make, Ads
# DjangoModelPermissionsOrAnonReadOnly

# Alert
class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


# Profile
class DjangoModelPermissionsOrAuthReadOnly(permissions.DjangoModelPermissionsOrAnonReadOnly):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return super(DjangoModelPermissionsOrAuthReadOnly, self).has_permission(request, view)
