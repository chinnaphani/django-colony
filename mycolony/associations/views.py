from django.shortcuts import render
from django.contrib.auth.decorators import login_required

#@login_required
def admin_dashboard_view(request):
    return render(request, 'associations/admin_dashboard.html')

def test_view(request):
    return render(request, 'base.html')