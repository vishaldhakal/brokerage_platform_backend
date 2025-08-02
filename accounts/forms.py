from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, UserProfile

class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for creating users in admin
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):
    """
    Custom form for changing users in admin
    """
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email')

class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile
    """
    class Meta:
        model = UserProfile
        fields = [
            'profile_image', 'address', 'city', 'state', 'zip_code', 'country',
            'business_description', 'years_in_business', 'linkedin_url',
            'facebook_url', 'twitter_url', 'instagram_url', 'email_notifications',
            'sms_notifications'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'business_description': forms.Textarea(attrs={'rows': 4}),
        } 