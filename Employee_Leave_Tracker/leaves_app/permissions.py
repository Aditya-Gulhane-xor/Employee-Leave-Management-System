from rest_framework import permissions 

class IsManager(permissions.BasePermission):

    def has_permission(self,request,view):
        if not request.user or not request.user.is_authenticated:
            return False 

        profile = getattr(request.user, 'profile',None)
        return bool(profile and profile.is_manager)

class IsEmployee(permissions.BasePermission):
    def has_permission(self,request,view):
        profile =getattr(request.user , 'profile',None)
        return bool(profile and not profile.is_manager)

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and (request.user.is_superuser or request.user.is_staff)
        )