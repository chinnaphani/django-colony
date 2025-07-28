from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AssociationMembership

@login_required(login_url='/web_login/')
def admin_dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('web_login')  # Safe fallback

    membership = AssociationMembership.objects.filter(user=request.user).first()
    association_name = membership.association.name if membership else "No Association"

    return render(request, 'associations/admin_dashboard.html', {
        'association_name': association_name
    })


#
# def test_view(request):
#     return render(request, 'base.html')
#
# def dashboard_view(request):
#     association_name = getattr(request.user.association, "name", "Your Association")
#     return render(request, 'dashboard.html', {
#
#     })