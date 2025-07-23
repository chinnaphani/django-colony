from django import forms
from .models import AssociationFeeType

class AssociationFeeTypeForm(forms.ModelForm):
    class Meta:
        model = AssociationFeeType
        exclude = ['association']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            #'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
