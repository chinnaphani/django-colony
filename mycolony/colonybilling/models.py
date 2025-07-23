from django.db import models
from associations.models import Association
from houses.models import House
from django.utils.timezone import now

class AssociationFeeType(models.Model):
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('one-time', 'One-Time')
    ])
    amount = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('association', 'name')

    def __str__(self):
        return f"{self.name} ({self.association.name})"




class PaymentRecord(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    fee_type = models.ForeignKey(AssociationFeeType, on_delete=models.CASCADE)
    amount = models.IntegerField()
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_on = models.DateField(null=True, blank=True)
    receipt_number = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('house', 'fee_type', 'due_date')

    def __str__(self):
        return f"{self.house} - {self.fee_type.name} - Due: {self.due_date}"

    def save(self, *args, **kwargs):
        if self.is_paid and not self.receipt_number:
            today_str = now().strftime("%Y%m%d")
            prefix = f"RCPT-{today_str}"

            # Count how many receipts were already generated today
            count_today = PaymentRecord.objects.filter(
                receipt_number__startswith=prefix
            ).count() + 1

            self.receipt_number = f"{prefix}-{count_today:03d}"  # e.g., RCPT-20250721-001

            if not self.paid_on:
                self.paid_on = now().date()

        super().save(*args, **kwargs)

class CorpusFundRecord(models.Model):
    house = models.OneToOneField('houses.House', on_delete=models.CASCADE)
    association = models.ForeignKey('associations.Association', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    is_paid = models.BooleanField(default=False)
    paid_on = models.DateField(null=True, blank=True)
    receipt_number = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.house.owner_name} - ₹{self.amount} - {'Paid' if self.is_paid else 'Unpaid'}"
