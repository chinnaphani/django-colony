from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import EmailMessage, get_connection
from django.utils.timezone import now
from datetime import date
from calendar import month_name
from django.db import IntegrityError
from django.utils import timezone
from mycolony import settings
from .models import PaymentRecord, AssociationFeeType,CorpusFundRecord
from .forms import AssociationFeeTypeForm
from houses.models import House
from .pdf_utils import generate_single_receipt, generate_advance_receipt,generate_single_receipt_corpus
from .utils import generate_receipt_number
from django.db import models



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


# @login_required
# def payment_list(request):
#     association = request.user.association
#     if not association:
#         return HttpResponseForbidden("No association linked to this user.")
#
#     houses = House.objects.filter(association=association)
#     payments = PaymentRecord.objects.filter(house__in=houses).order_by('-due_date')
#
#     return render(request, 'colonybilling/templates/colonybilling/payment_List.html', {
#         'payments': payments
#     })

@login_required
def payment_list(request):
    association = getattr(request.user, 'association', None)
    if not association:
        return HttpResponseForbidden("No association linked to this user.")

    houses = House.objects.filter(association=association)

    today = timezone.now().date()
    payments = PaymentRecord.objects.filter(
        house__in=houses,
        is_paid=False,
    ).annotate(
        is_overdue=models.Case(
            models.When(is_paid=True, then=models.Value(False)),
            models.When(due_date__lt=today, then=models.Value(True)),
            default=models.Value(False),
            output_field=models.BooleanField()
        )
    ).order_by('-due_date')

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
        payment.receipt_number = generate_receipt_number(payment.house.association, PaymentRecord)
        payment.save()

        pdf_file = generate_single_receipt(payment)

        if payment.house.email and pdf_file:
            email = EmailMessage(
                subject="Your Payment Receipt",
                body="Dear Resident,\n\nPlease find your payment receipt attached.\n\nThanks,\nAdmin",
                from_email="chinnaphani@gmail.com",  # Or use settings.DEFAULT_FROM_EMAIL
                reply_to=[payment.house.association.email] if payment.house.association.email else None,
                to=[payment.house.email],
            )
            email.attach(f"receipt_{payment.receipt_number}.pdf", pdf_file, "application/pdf")
            email.send(fail_silently=False)

    return redirect("colonybilling:payment-list")


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
            receipt_no = generate_receipt_number(association, PaymentRecord) if mark_paid else None

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

@login_required
def corpus_fund_list_view(request):
    user = request.user
    association = user.association
    records = CorpusFundRecord.objects.filter(association=association)
    return render(request, 'colonybilling/corpus_fund_list.html', {'records': records})

# @login_required
# def mark_corpus_paid(request, pk):
#     record = get_object_or_404(
#         CorpusFundRecord,
#         pk=pk,
#         association=request.user.association
#     )
#
#     if request.method == 'POST':
#         if not record.is_paid:
#             record.is_paid = True
#             record.paid_on = now().date()
#             record.receipt_number = generate_receipt_number(
#                 record.association, CorpusFundRecord
#             )
#             record.save()
#             messages.success(request, "✅ Marked as paid and receipt generated.")
#         else:
#             messages.info(request, "ℹ️ This record is already marked as paid.")
#
#     return redirect('colonybilling:corpus-fund-list')

@login_required
def mark_corpus_paid(request, pk):
    record = get_object_or_404(
        CorpusFundRecord,
        pk=pk,
        association=request.user.association
    )

    if request.method == 'POST':
        if not record.is_paid:
            record.is_paid = True
            record.paid_on = now().date()
            record.receipt_number = generate_receipt_number(
                record.association, CorpusFundRecord
            )
            record.save()

            # ✅ Send receipt via email if house has email
            house = record.house
            if house.email:
                try:
                    pdf_file = generate_single_receipt_corpus(house, record.amount, record.receipt_number)
                    email = EmailMessage(
                        subject="Your Corpus Fund Receipt",
                        body=(
                            f"Dear {house.owner_name},\n\n"
                            f"Thank you for your corpus fund payment.\n"
                            f"Receipt No: {record.receipt_number}\n"
                            f"Amount: ₹{record.amount}\n\n"
                            f"Regards,\nAdmin"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        reply_to=[house.association.email],
                        to=[house.email],
                    )
                    email.attach(f"receipt_{record.receipt_number}.pdf", pdf_file, "application/pdf")
                    email.send(fail_silently=False)
                    print("✅ Email sent for corpus fund payment")
                except Exception as e:
                    print("❌ Email failed:", e)

            messages.success(request, "✅ Marked as paid, receipt generated, and emailed.")
        else:
            messages.info(request, "ℹ️ This record is already marked as paid.")

    return redirect('colonybilling:corpus-fund-list')

