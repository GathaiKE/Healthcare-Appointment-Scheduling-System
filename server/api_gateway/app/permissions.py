
class BasePermissions():
    pass

class IsSuperAdmin(BasePermissions):
    pass

class IsAdminOrOwner(BasePermissions):
    pass

class IsStaff(BasePermissions):
    pass

class IsStaffOrOwner(BasePermissions):
    pass