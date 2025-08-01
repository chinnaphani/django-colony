from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AssociationMembership

@login_required(login_url='/web_login/')
def admin_dashboard_view(request):
    print(f"🔍 Admin dashboard accessed by: {request.user.username}")
    
    membership = AssociationMembership.objects.filter(user=request.user).first()
    
    # Debug: Check if membership exists
    if not membership:
        print(f"❌ No membership found for user: {request.user.username}")
        return render(request, 'associations/admin_dashboard.html', {
            'association_name': "No Association"
        })
    
    # Debug: Check if association exists
    if not membership.association:
        print(f"❌ No association found for membership: {membership}")
        return render(request, 'associations/admin_dashboard.html', {
            'association_name': "No Association"
        })
    
    association_name = membership.association.name
    print(f"✅ User: {request.user.username}, Association: {association_name}")

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