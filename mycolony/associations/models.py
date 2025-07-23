from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

CustomUser = get_user_model()  # Safely reference the custom user model

def generate_registration_number():
    last = Association.objects.order_by('id').last()
    if last and last.registration_number:
        try:
            last_num = int(last.registration_number.split('-')[-1])
        except ValueError:
            last_num = 0
    else:
        last_num = 0
    return f"REG-{str(last_num + 1).zfill(4)}"


class Association(models.Model):
    name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=50, unique=True, blank=True)

    # Address fields
    address_line = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    # Contact details
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    membership_date = models.DateField(default=timezone.now)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.registration_number:
            self.registration_number = generate_registration_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.city} ({self.registration_number})"


class AssociationMembership(models.Model):  # ✅ Use models.Model here
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('MEMBER', 'Member'),
        ('STAFF', 'Staff')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'association')

    def __str__(self):
        return f"{self.user.username} - {self.association.name} ({self.role})"
