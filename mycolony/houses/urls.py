from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.members_view, name='members'),
    path('members/<int:pk>/edit/', views.edit_house_view, name='edit_house'),
    path('members/<int:pk>/delete/', views.delete_house, name='delete_house'),  # ✅ fixed line
    path('members/create/', views.create_house_view, name='create_house'),
]
