from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        if not user.is_active:
            messages.error(self.request, "Your user account is inactive. Please contact the support team.")
            return render(self.request, self.template_name, {'form': form})

        if not hasattr(user, 'association') or user.association is None:
            messages.error(self.request, "You are not assigned to any association. Contact admin.")
            return render(self.request, self.template_name, {'form': form})

        if not user.association.active:
            messages.error(self.request, "Your association is inactive. Login denied. Contact support.")
            return render(self.request, self.template_name, {'form': form})

        login(self.request, user)
        return redirect(self.get_success_url())