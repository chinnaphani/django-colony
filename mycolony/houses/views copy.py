from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from .models import House
from .forms import HouseForm,HouseCreateForm
from colonybilling.views import generate_receipt_number
from colonybilling.models import CorpusFundRecord
from django.utils.timezone import now
from colonybilling.pdf_utils import generate_single_receipt_corpus
from django.core.mail import EmailMessage
from mycolony import settings


@login_required
def members_view(request):
    association = request.user.association
    if not association:
        return HttpResponseForbidden("No association assigned to this user.")

    houses = House.objects.filter(association=association)
    return render(request, 'houses/members.html', {'houses': houses})


@login_required
def edit_house_view(request, pk):
    association = request.user.association
    if not association:
        return HttpResponseForbidden("No association assigned to this user.")

    house = get_object_or_404(House, pk=pk, association=association)

    if request.method == 'POST':
        form = HouseForm(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Member updated successfully!")
            return redirect('members')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = HouseForm(instance=house)

    return render(request, 'houses/edit_house.html', {
        'form': form,
        'house': house
    })


@require_POST
@login_required
def delete_house(request, pk):
    association = request.user.association
    if not association:
        return HttpResponseForbidden("No association assigned to this user.")

    house = get_object_or_404(House, pk=pk, association=association)
    house.delete()
    messages.success(request, "🏡 Member deleted successfully.")
    return redirect('members')


@login_required
def create_house_view(request):
    user = request.user
    association = user.association

    if request.method == 'POST':
        form = HouseCreateForm(request.POST)
        if form.is_valid():
            house = form.save(commit=False)
            house.association = association
            house.save()

            # 🌟 Handle corpus fund payment
            corpus_paid = form.cleaned_data.get('corpus_fund_paid')
            corpus_amount = association.corpus_fund

            record_data = {
                "house": house,
                "association": association,
                "amount": corpus_amount,
                "is_paid": corpus_paid,
                "paid_on": now().date() if corpus_paid else None,
            }

            if corpus_paid:
                receipt_no = generate_receipt_number(association, CorpusFundRecord)
                record_data["receipt_number"] = receipt_no

            # ✅ Create the CorpusFundRecord
            record = CorpusFundRecord.objects.create(**record_data)

            # ✅ Send receipt email only if paid
            if corpus_paid and house.email:
                try:

                    pdf_file = generate_single_receipt_corpus(house, corpus_amount, receipt_no)
                    email = EmailMessage(
                        subject=f"🌸 Welcome to  Residents' Association!",
                        body=(
                            f"Dear {house.owner_name},\n\nThank you for your one-time joining fee.\n"
                            f"Receipt No: {receipt_no}\nAmount: ₹{corpus_amount}\n\nRegards,\nAdmin"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        reply_to=[house.association.email],
                        to=[house.email],
                    )
                    email.attach(f"receipt_{receipt_no}.pdf", pdf_file, "application/pdf")
                    email.send(fail_silently=False)
                except Exception as e:
                    print("❌ Email failed:", e)

            messages.success(request, "✅ Member created successfully.")
            return redirect('members')

        else:
            # ✅ FORM INVALID — return the page with errors
            return render(request, 'houses/create_house.html', {'form': form})

    else:
        form = HouseCreateForm()

    return render(request, 'houses/create_house.html', {'form': form})