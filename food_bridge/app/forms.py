from django import forms
from .models import CustomUser, FoodDonation, NGOProfile
from django.contrib.auth.models import User

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'role', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class FoodDonationForm(forms.ModelForm):
    class Meta:
        model = FoodDonation
        fields = ['event_name', 'food_type', 'quantity', 'unit', 'pickup_address', 'pickup_deadline']
        widgets = {
            'event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event name'}),
            'food_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'kg/liters'}),
            'pickup_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Pickup address'}),
            'pickup_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class NGOProfileForm(forms.ModelForm):
    class Meta:
        model = NGOProfile
        fields = ['organization_name', 'phone_number', 'address']
        widgets = {
            'organization_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}),
        }

class NGOUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
        }
