from django.db import models
import uuid

class Patient(models.Model):
    id=models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user_ref_id=models.CharField(blank=False)
    created_at=models.DateTimeField(auto_now_add=True, blank=False)
    deleted_at=models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Patient {self.user_ref_id}"

