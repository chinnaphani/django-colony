from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.get_full_name()} ({self.email})"

    @property
    def association(self):
        # Assumes each user belongs to only one association (you can change this logic)
        membership = self.associationmembership_set.first()
        return membership.association if membership else None