from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from .models import House
from .forms import HouseForm


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
            messages.success(request, "✅ House updated successfully!")
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
    messages.success(request, "🏡 House deleted successfully.")
    return redirect('members')
