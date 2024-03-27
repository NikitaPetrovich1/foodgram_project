from rest_framework import permissions


class IsAuthenticatedForMeOrAllowAny(permissions.BasePermission):

    def has_permission(self, request, view):
        if 'me' in request.path:
            return request.user.is_authenticated
        return True
