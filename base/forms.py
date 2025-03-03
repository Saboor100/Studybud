from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model  # Correct import for forms
from .models import Room, message  # Ensure this import is correct

User = get_user_model()  # Correct assignment for forms

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username','email', 'password1', 'password2']

class Userform(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'username', 'email', 'bio']

class MessageForm(forms.ModelForm):  # Correct definition
    class Meta:
        model = message
        fields = ['body', 'file']
        widgets = {
            'body': forms.TextInput(attrs={'placeholder': 'Write your message here...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        body = cleaned_data.get('body')
        file = cleaned_data.get('file')

        if not body and not file:
            raise forms.ValidationError("You must provide either a message or a file.")

        return cleaned_data