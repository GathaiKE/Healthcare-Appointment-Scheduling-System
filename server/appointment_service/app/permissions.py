from rest_framework.permissions import BasePermission
import logging

logger=logging.getLogger(__name__)

    
class RolePermission(BasePermission):
    ROLE_HIERACHY={
        'admin':3,
        'doctor':2,
        'patient':1,
        'public':0
    }

    allowed_roles={'patient', 'doctor'}
    min_role_level=None

    def has_permission(self, request, view):
        role=request.user.role
        roles=self.get_effective_roles(role)
        if not roles.isdisjoint(self.allowed_roles):
            return True
        if self.min_role_level is not None:
            return self.ROLE_HIERACHY.get(role, 0) >= self.min_role_level
        return False
    
    def get_effective_roles(self, role):
        user_role_level = self.ROLE_HIERACHY.get(role, 0)
    
        effective_roles = set()
        for role_name, role_level in self.ROLE_HIERACHY.items():
            if role_level <= user_role_level:
                effective_roles.add(role_name)
        return effective_roles
        
class IsPatientDoctor(RolePermission):
    allowed_roles={'patient', 'doctor'}
    # min_role_level=RolePermission.ROLE_HIERACHY['patient']

class IsPatient(RolePermission):
    allowed_roles={'patient'}
    # min_role_level=RolePermission.ROLE_HIERACHY['patient']


class IsDoctor(RolePermission):
    allowed_roles={'doctor'}
    min_role_level=RolePermission.ROLE_HIERACHY['doctor']