from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save
from django.db.models import Q
from django.core.exceptions import ValidationError

from .models import Patient, Guardianship

@receiver(signal=post_delete, sender=Patient)
def delete_next_of_kin(sender, instance, **kwargs):
    if instance.next_of_kin:
        instance.next_of_kin.delete()
        
@receiver(signal=pre_save, sender=Guardianship)
def validate_guardian_limit(sender, instance, **kwargs):
    if instance.relationship=='guardian':
        existing_guardians=instance.dependent.guardian_set.filter(Q(relationship='guardian')).count()
        if existing_guardians >=2:
            raise ValidationError("Max 2 guardians allowed")
        