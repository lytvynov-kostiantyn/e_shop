from django import forms
from .models import Comments, User


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        max_length=20,
        min_length=5,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    confirmation = forms.CharField(
        max_length=20,
        min_length=5,
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


# form for commit input
class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment']
        labels = {
            'comment': ''
        }
        widgets = {
            'comment': forms.Textarea(attrs={"class": "form-control", "rows": 4})
        }


# form for user info input 
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'address', 'phone_number']
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email address',
            'address': 'Address',
            'phone_number': 'Phone number',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={"class": "form-control"}),
            'last_name': forms.TextInput(attrs={"class": "form-control"}),
            'email': forms.EmailInput(attrs={"class": "form-control"}),
            'address': forms.TextInput(attrs={"class": "form-control"}),
            'phone_number': forms.NumberInput(attrs={'class': 'form-control'})
        }
