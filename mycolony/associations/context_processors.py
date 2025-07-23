def user_role_context(request):
    from associations.models import AssociationMembership  # ✅ Move import inside function
    role = None
    if request.user.is_authenticated:
        membership = AssociationMembership.objects.filter(user=request.user).first()
        if membership:
            role = membership.role
    return {'user_role': role}
