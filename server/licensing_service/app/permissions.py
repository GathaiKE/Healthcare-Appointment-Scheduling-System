from rest_framework.permissions import BasePermission
import logging
from django.contrib.auth.models import AnonymousUser

logger=logging.getLogger(__name__)

    
class RolePermission(BasePermission):
    ROLE_HIERACHY={
        'admin':2,
        'doctor':1,
        'public':0
    }

    def __init__(self):
        self.allowed_roles={'doctor'}
        self.min_role_level=None

    def has_permission(self, request, view):
        if not request.user or isinstance(request.user, AnonymousUser):
            logger.warning("Unauthenticated access attempt")
            return self._handle_public_access()

        role=getattr(request.user, "role", "public")

        if self._has_explicit_permission(role):
            return True
        
        
        if role not in self.ROLE_HIERACHY:
            logger.error(f"Invalid role: '{role}' from user '{request.user.id}'.")
            return False
        
        if self.min_role_level is not None:
            return self._has_hierarchy_permission(role)
        
        return False
    

    def has_object_permission(self, request, view, obj):
        if not request.user or isinstance(request.user, AnonymousUser):
            logger.warning("Unauthenticated access attempt")
            return self._handle_public_access()

        if request.user.role == 'doctor':
            user_id=getattr(request.user, 'id', None)

            if not user_id:
                logger.error("Doctor not found")
                return False
            
            ownership=getattr(obj, 'prefetched_ownership', [None])[0]
            if not ownership:
                try:
                    ownership=obj.record_ownership_set.first()
                except AttributeError:
                    logger.error("Medical record missing ownership relation")
                    return False
                
            return str(ownership.doctor_id) == str(user_id)
        
        return False
    
    def _handle_public_access(self):
        if 'public' in self.allowed_roles:
            logger.info("Granting public access!")
            return True
        return False
    
    def _has_explicit_permission(self, role):
        return bool(set(self.get_effective_roles(role)) & set(self.get_allowed_roles()))
    
    def get_allowed_roles(self):
        return set()
    
    def _has_hierarchy_permission(self, role):
        return self.ROLE_HIERACHY.get(role, 0) >= self.min_role_level
    
    def get_effective_roles(self, role):
        user_role_level = self.ROLE_HIERACHY.get(role, 0)
    
        return (
            r for r, level in self.ROLE_HIERACHY.items()
            if level <= user_role_level
        )

class IsOwnerOrDoctor(RolePermission):
    def __init__(self):
        super().__init__()
        self.allowed_roles={'doctor'}
        self.min_role_level = self.ROLE_HIERACHY['doctor']

    def has_object_permission(self, request, view, obj):
        if super().has_permission(request, view):
            return True
        return super().has_object_permission(request, view, obj)
    
    def get_allowed_roles(self):
        return {'doctor'}

class IsDoctor(RolePermission):
    def __init__(self):
        super().__init__()
        self.allowed_roles={'doctor'}
        self.allowed_roles=self.ROLE_HIERACHY['doctor']

    def get_allowed_roles(self):
        return {'doctor'}


class IsAdminUser(RolePermission):
    def __init__(self):
        super().__init__()
        self.allowed_roles={'admin'}
        self.min_role_level = self.ROLE_HIERACHY['admin']

    def get_allowed_roles(self):
        return {'admin'}