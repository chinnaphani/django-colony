from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from rest_framework.authtoken.views import obtain_auth_token
from associations.views import admin_dashboard_view

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Dashboard Views
    path('admin-dashboard/', admin_dashboard_view, name='admin-dashboard'),

    # Core site URLs
    path('', include('core.urls')),

    # Houses app
    path('mmembers/', include('houses.urls')),

    # Billing module
    path('billing/', include('colonybilling.urls')),

    # Logout
    path('accounts/logout/', LogoutView.as_view(next_page='web_login'), name='logout'),

    # Android API
    path('api/', include('andriodapi.urls')),

    # Token Authentication
    path('api/api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
