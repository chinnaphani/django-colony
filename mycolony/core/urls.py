from django.urls import path
from .views import CustomLoginView, homepage_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', homepage_view, name='home'),
    path('web_login/', CustomLoginView.as_view(), name='web_login'),
    path('logout/', LogoutView.as_view(next_page='web_login'), name='logout'),
]
