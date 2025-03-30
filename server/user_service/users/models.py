from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12, unique=True, blank=True)
    first_name = models.CharField(null=True)
    last_name = models.CharField(null=True)
    surname = models.CharField(null=True)
    username = None

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    def __str__ (self):
        full_name:str = "{self.first_name} {self.last_name} {self.surname}"
        return full_name