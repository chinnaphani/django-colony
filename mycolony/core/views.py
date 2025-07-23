from django import forms
from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from associations.models import AssociationMembership
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

# Get the active user model
UserModel = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Please enter a correct username and password.",
        'inactive': "Your account is inactive. Please contact support.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'autofocus': True})

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # First check if user exists (without authentication)
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
                if not user.is_active:
                    raise ValidationError(
                        self.error_messages['inactive'],
                        code='inactive',
                    )
            except UserModel.DoesNotExist:
                pass  # Will be handled by authenticate()

            # Then authenticate
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )

            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )

        return self.cleaned_data




class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()

        # Check association memberships
        memberships = AssociationMembership.objects.select_related('association').filter(user=user)

        if not memberships.exists():
            messages.error(self.request, "You are not assigned to any association. Contact admin.")
            return self.render_to_response(self.get_context_data(form=form))

        if not any(m.association and getattr(m.association, 'active', True) for m in memberships):
            messages.error(self.request, "Your association is inactive. Login denied. Contact support.")
            return self.render_to_response(self.get_context_data(form=form))

        login(self.request, user)
        return redirect(self.get_success_url())


def get_success_url(self):
    user = self.request.user

    # Get first valid active membership (or handle multiple if needed)
    membership = AssociationMembership.objects.select_related('association').filter(
        user=user,
        association__active=True
    ).first()

    if membership:
        if membership.role == 'ADMIN':
            return reverse('admin_dashboard')  # e.g., URL name for admin
        elif membership.role == 'STAFF':
            return reverse('staff_dashboard')
        elif membership.role == 'MEMBER':
            return reverse('member_dashboard')

    # Fallback if none match
    messages.error(self.request, "No valid association membership found.")
    return reverse('login')