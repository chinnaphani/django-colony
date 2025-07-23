from django import forms
from .models import House

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['owner_name','house_number', 'email', 'phone_number', 'active']

        labels = {
            'owner_name': 'Full Name',  # 🔁 Change this to your desired label
            'house_number': 'House Number',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'is_active': 'Active',
        }

class HouseCreateForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['owner_name','house_number', 'email', 'phone_number', 'corpus_fund_paid']

        labels = {
            'owner_name': 'Full Name',  # 🔁 Change this to your desired label
            'house_number': 'House Number',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'corpus_fund_paid': 'Corpus Fund Paid:',
        }

    corpus_fund_paid = forms.BooleanField(
        required=False,
        label="Mark Corpus Fund as Paid"
    )
