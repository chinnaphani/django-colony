from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import EmailMessage, get_connection
from django.utils.timezone import now
from datetime import date
from calendar import month_name
from django.db import IntegrityError

from mycolony import settings
from .models import PaymentRecord, AssociationFeeType
from .forms import AssociationFeeTypeForm
from houses.models import House
from .pdf_utils import generate_single_receipt, generate_advance_receipt


@login_required
def association_fee_settings(request, fee_id=None):
    association = request.user.association
    if not association:
        return HttpResponseForbidden("User is not linked to any association.")

    fee_instance = get_object_or_404(AssociationFeeType, id=fee_id, association=association) if fee_id else None

    if request.method == 'POST':
        form = AssociationFeeTypeForm(request.POST, instance=fee_instance)
        if form.is_valid():
            fee_type = form.save(commit=False)
            fee_type.association = association
            fee_type.is_active = True
            fee_type.save()
            return redirect('colonybilling:association_fee_settings')
    else:
        form = AssociationFeeTypeForm(instance=fee_instance)

    fee_types = AssociationFeeType.objects.filter(association=association)

    return render(request, 'colonybilling/association_fee_settings.html', {
        'form': form,
        'fee_types': fee_types,
        'editing': fee_instance is not None,
        'fee_id': fee_id
    })


@login_required
def delete_association_fee(request, fee_id):
    association = request.user.association
    fee = get_object_or_404(AssociationFeeType, id=fee_id, association=association)

    if request.method == 'POST':
        fee.delete()
        messages.success(request, "Fee type deleted successfully.")
        return redirect('colonybilling:association_fee_settings')

    return HttpResponseForbidden("Invalid request.")


@login_required
def payment_list(request):
    association = request.user.association
    if not association:
        return HttpResponseForbidden("No association linked to this user.")

    houses = House.objects.filter(association=association)
    payments = PaymentRecord.objects.filter(house__in=houses).order_by('-due_date')

    return render(request, 'colonybilling/payment_list.html', {
        'payments': payments
    })


@login_required
def mark_payment_as_paid(request, pk):
    payment = get_object_or_404(PaymentRecord, pk=pk)

    if payment.house.association != request.user.association:
        return HttpResponseForbidden("❌ Not allowed")

    if request.method == 'POST' and not payment.is_paid:
        payment.is_paid = True
        payment.paid_on = now().date()
        payment.receipt_number = generate_receipt_number(payment.house.association)
        payment.save()

        pdf_file = generate_single_receipt(payment)

        if payment.house.email and pdf_file:
            email = EmailMessage(
                subject="Your Payment Receipt",
                body="Dear Resident,\n\nPlease find your payment receipt attached.\n\nThanks,\nAdmin",
                from_email="chinnaphani@gmail.com",
                to=[payment.house.email],
            )
            email.attach(f"receipt_{payment.receipt_number}.pdf", pdf_file, "application/pdf")
            email.send(fail_silently=False)

    return redirect("colonybilling:payment-list")


def generate_receipt_number(association):
    today_str = date.today().strftime('%Y%m%d')
    prefix = "RCPT"

    last = PaymentRecord.objects.filter(
        house__association=association,
        receipt_number__startswith=f"{prefix}-{today_str}"
    ).order_by('-receipt_number').first()

    last_num = 0
    if last and last.receipt_number:
        try:
            last_num = int(last.receipt_number.split('-')[-1])
        except ValueError:
            pass

    return f"{prefix}-{today_str}-{last_num + 1:03d}"


@login_required
def create_advance_payment(request):
    msg = None
    association = request.user.association
    if not association:
        return HttpResponseForbidden("User has no linked association.")

    if request.method == "POST":
        house_id = request.POST.get("house_id")
        fee_id = request.POST.get("fee_type_id")
        months = request.POST.getlist("months")
        year = int(request.POST.get("year", now().year))
        mark_paid = request.POST.get("mark_paid") == "on"

        if not (house_id and fee_id and months):
            msg = "⚠️ Please select a house, a fee type, and at least one month."
        else:
            house = get_object_or_404(House, id=house_id)
            fee = get_object_or_404(AssociationFeeType, id=fee_id)

            created = updated = 0
            paid_months = []
            total_amount = 0
            receipt_no = generate_receipt_number(house.association) if mark_paid else None

            for m in months:
                month_num = int(m)
                due_date = date(year, month_num, 10)

                try:
                    obj, made = PaymentRecord.objects.get_or_create(
                        house=house,
                        fee_type=fee,
                        due_date=due_date,
                        defaults={
                            "amount": fee.amount,
                            "is_paid": mark_paid,
                            "paid_on": now().date() if mark_paid else None,
                            "receipt_number": receipt_no if mark_paid else None,
                        },
                    )
                except IntegrityError:
                    continue

                updated_this_month = False

                if made:
                    created += 1

                if mark_paid and (not obj.is_paid or not obj.receipt_number):
                    obj.is_paid = True
                    obj.paid_on = now().date()
                    obj.receipt_number = receipt_no
                    obj.save(update_fields=["is_paid", "paid_on", "receipt_number"])
                    updated += 1
                    updated_this_month = True

                if made or updated_this_month:
                    paid_months.append(month_num)
                    total_amount += fee.amount

            print(f"🔍 mark_paid: {mark_paid}")
            print(f"🔍 paid_months: {paid_months}")
            print(f"🔍 house.email: {house.email}")
            print(f"🔍 receipt_no: {receipt_no}")

            if mark_paid and paid_months and house.email and receipt_no:
                paid_months_sorted = sorted(set(paid_months))

                month_list_str = ", ".join([month_name[m] for m in paid_months_sorted])

                pdf_file = generate_advance_receipt(house, fee, month_list_str, year, total_amount, receipt_no)


                if pdf_file:
                    try:
                        connection = get_connection(fail_silently=False)
                        email = EmailMessage(
                            subject=f"Advance Payment Receipt - {receipt_no}",
                            body=(
                                f"Dear {house.owner_name},\n\n"
                                f"Thank you for your advance payment for the following months of {year}: {month_list_str}.\n"
                                f"Receipt Number: {receipt_no}\n"
                                f"Total Paid: ₹{total_amount}\n\n"
                                f"Regards,\nAdmin Team"
                            ),
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            reply_to=[house.association.email],
                            to=[house.email],
                            connection=connection
                        )


                        email.attach(f"advance_receipt_{receipt_no}.pdf", pdf_file, "application/pdf")
                        email.send()
                        print("✅ Email sent")
                    except Exception as e:
                        print(f"❌ Email sending failed: {e}")
                else:
                    print("❌ PDF generation failed.")

            msg = f"✅ {created} payments created, {updated} updated." if created or updated else "⚠️ All selected months already have payments."

    context = {
        "houses": House.objects.filter(association=association, active=True),
        "fees": AssociationFeeType.objects.filter(association=association),
        "months": [(i, month_name[i]) for i in range(1, 13)],
        "current_year": now().year,
        "msg": msg,
    }

    return render(request, "colonybilling/advance_payment_form.html", context)

