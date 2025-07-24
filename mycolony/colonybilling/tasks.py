from celery import shared_task
from datetime import date
from django.utils.timezone import now
from .models import PaymentRecord, AssociationFeeType
from houses.models import House




def recurring_fee_logic(month=None, year=None):
    today = date.today()
    month = month or today.month
    year = year or today.year

    billing_month = date(year, month, 1)
    due_date = date(year, month, 10)
    created_count = 0

    fee_types = AssociationFeeType.objects.filter(is_active=True)

    for fee_type in fee_types:
        if fee_type.frequency != 'monthly':
            continue

        houses = House.objects.filter(association=fee_type.association, active=True)

        for house in houses:
            obj, created = PaymentRecord.objects.get_or_create(
                house=house,
                fee_type=fee_type,
                due_date=due_date,
                defaults={
                    'amount': fee_type.amount,
                    'is_paid': False,
                }
            )
            if created:
                created_count += 1

    print(f"✅ Created {created_count} PaymentRecords for {billing_month:%B %Y}")

# ✅ Fix: Add `bind=True` and `self` so Celery can call it with kwargs
@shared_task(bind=True)
def generate_recurring_fees(self, *args, **kwargs):
    month = kwargs.get('month')
    year = kwargs.get('year')
    return recurring_fee_logic(month=month, year=year)


# @shared_task
# def generate_recurring_fees():
#     today = date.today()
#     billing_month = date(today.year, today.month, 1)
#     due_date = date(today.year, today.month, 10)
#
#     created_count = 0
#
#     fee_types = AssociationFeeType.objects.filter(is_active=True)
#
#     for fee_type in fee_types:
#         if fee_type.frequency != 'monthly':
#             continue
#
#         houses = House.objects.filter(association=fee_type.association, active=True)
#
#         for house in houses:
#             obj, created = PaymentRecord.objects.get_or_create(
#                 house=house,
#                 fee_type=fee_type,
#                 due_date=due_date,
#                 defaults={
#                     'amount': fee_type.amount,
#                     'is_paid': False,
#                 }
#             )
#             if created:
#                 created_count += 1
#
#     print(f"✅ Celery Task: {created_count} PaymentRecords created for {billing_month:%B %Y}")

@shared_task
def create_onetime_fees():
    for house in House.objects.filter(active=True):
        fee_types = AssociationFeeType.objects.filter(association=house.association, frequency='ONETIME')
        for fee in fee_types:
            PaymentRecord.objects.get_or_create(
                house=house,
                fee_type=fee,
                due_date=now().date(),
                defaults={
                    'amount': fee.amount,
                    'is_paid': False,
                }
            )
