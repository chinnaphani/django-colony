from django.db import models
from django.utils.timezone import now
from associations.models import Association
from django.utils.timezone import now
from django.utils import timezone
# Create your models here.

def current_date():
    return now().date()

class House(models.Model):
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    house_number = models.CharField(max_length=50)
    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)

    membership_number = models.CharField(max_length=50, unique=True, blank=True)
    membership_date = models.DateField(default=current_date)
    active = models.BooleanField(default=True)

    house_type = models.CharField(max_length=50, choices=[
        ("individual", "Individual"),
        ("apartment", "Apartment"),
        ("mall", "Mall")
    ])
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.house_number} - {self.owner_name}"

    def save(self, *args, **kwargs):
        if not self.membership_number:
            prefix = self.association.registration_number or "REG-0000"
            count = House.objects.filter(association=self.association).count() + 1
            self.membership_number = f"{prefix}-{count:03d}"
        super().save(*args, **kwargs)
