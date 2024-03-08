from django import forms
from django.contrib.auth.models import User 
from ratearant.models import UserProfile
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password',
                  'email', 'first_name','last_name')
        
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                "This username is already taken. Please choose another one."
                )
        return username