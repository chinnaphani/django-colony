from django.urls import path
from .views import CustomLoginView, homepage_view
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

urlpatterns = [
    path('', homepage_view, name='home'),
    path(
        'web_login/',
        ensure_csrf_cookie(CustomLoginView.as_view(template_name='core/login.html')),
        name='web_login'
    )

    # Add more paths as needed
]
