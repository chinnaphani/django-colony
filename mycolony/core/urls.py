from django.urls import path
from .views import CustomLoginView
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),  # 👈 root

    path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),


]
