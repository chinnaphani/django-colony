from django.urls import path
from .views import CustomLoginView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='home'),  # 👈 root

]
