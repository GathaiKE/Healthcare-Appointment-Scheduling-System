from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff
    
class IsPatientsDoctor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.patient_visit.doctor