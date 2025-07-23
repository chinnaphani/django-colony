from django.urls import path
from .views import admin_dashboard_view

urlpatterns = [
    path('admin-dashboard/', admin_dashboard_view, name='admin-dashboard'),
    # path('test/', test_view, name='test-view'),

]
