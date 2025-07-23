from django import forms
from .models import House

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['house_number', 'owner_name', 'email', 'phone_number', 'active']
