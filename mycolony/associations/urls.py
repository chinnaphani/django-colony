from django.urls import path, include
from .views import admin_dashboard_view, test_dashboard_view

urlpatterns = [
    path('admin-dashboard/', admin_dashboard_view, name='admin-dashboard'),
    # path('test/', test_view, name='test-view'),
    path('', include('core.urls')),  # or wherever the dashboards are defined

]
