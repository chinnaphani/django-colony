from django import forms
from django.contrib import messages
from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.shortcuts import render, redirect
from django.urls import reverse
from associations.models import AssociationMembership
from django.contrib.auth import authenticate

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
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
                if not user.is_active:
                    raise ValidationError(self.error_messages['inactive'], code='inactive')
            except UserModel.DoesNotExist:
                pass

            self.user_cache = authenticate(self.request, username=username, password=password)

            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )

        return self.cleaned_data


@method_decorator(csrf_protect, name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
@method_decorator(sensitive_post_parameters(), name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        
        memberships = AssociationMembership.objects.select_related('association').filter(user=user)

        if not memberships.exists():
            messages.error(self.request, "You are not assigned to any association. Contact admin.")
            return self.render_to_response(self.get_context_data(form=form))

        if not any(m.association and getattr(m.association, 'active', True) for m in memberships):
            messages.error(self.request, "Your association is inactive. Login denied. Contact support.")
            return self.render_to_response(self.get_context_data(form=form))

        # Perform login
        login(self.request, user)
        
        # Ensure session is saved
        self.request.session.save()
        
        # Set session as modified to ensure it's saved
        self.request.session.modified = True
        
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        membership = AssociationMembership.objects.select_related('association').filter(
            user=user,
            association__active=True
        ).first()

        if membership:
            if membership.role == 'ADMIN':
                return '/admin-dashboard/'
            elif membership.role == 'STAFF':
                return reverse('staff-dashboard')
            elif membership.role == 'MEMBER':
                return reverse('member-dashboard')

        logout(self.request)
        messages.error(self.request, "You are not assigned to any active association.")
        return reverse('web_login')


@ensure_csrf_cookie
def homepage_view(request):
    return render(request, 'core/home.html')
