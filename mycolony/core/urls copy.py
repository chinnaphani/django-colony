from django.urls import path,include
from .views import CustomLoginView,homepage_view
from django.contrib.auth.views import LoginView

# urlpatterns = [
#     path('', CustomLoginView.as_view(), name='web_login'),  # 👈 root
#     path('', homepage_view, name='home'),
#     path('web_login/', CustomLoginView.as_view(template_name='core/login.html'), name='web_login'),
#     path('profile/', profile_view, name='profile'),
#     path('houses/', add_house, name='add_house'),
#
# ]
urlpatterns = [
    path('', homepage_view, name='home'),  # 👈 homepage
    path('web_login/', CustomLoginView.as_view(template_name='core/login.html'), name='web_login'),

]
