# api/urls.py
from django.urls import path, include
from .views import add_house,profile_view,get_house_by_mobile,HouseViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'houses', HouseViewSet, basename='house')
urlpatterns = [


    path('houses/', add_house, name='add_house_api'),

    path('profile/', profile_view, name='profile'),

    path('houses/by_mobile/', get_house_by_mobile, name='get_house_by_mobile'),

    path('', include(router.urls)),
]

