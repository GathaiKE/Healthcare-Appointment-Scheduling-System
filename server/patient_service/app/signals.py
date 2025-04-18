from django.dispatch import receiver
from django.db.models.signals import post_delete

from .models import Patient
@receiver(signal=post_delete, sender=Patient)
def delete_next_of_kin(sender, instance, **kwargs):
    if instance.next_of_kin:
        instance.next_of_kin.delete()
        