from django import forms  # Correct import for forms
from .models import Room, User, message  # Ensure this import is correct

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']

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