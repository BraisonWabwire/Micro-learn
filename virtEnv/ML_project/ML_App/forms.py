from django import forms
from django.forms.widgets import PasswordInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update password1 and password2 fields' widgets for custom placeholders
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Firstname'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Lastname'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            # The placeholders for password fields are set in the __init__ method now
        }



from django import forms
from .models import Instructor
from django.contrib.auth.models import User

class InstructorForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, help_text="Username for login")
    password = forms.CharField(widget=forms.PasswordInput(), required=True, help_text="Set a password")

    class Meta:
        model = Instructor
        fields = ['username', 'password', 'name', 'email', 'department']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )
        instructor = super().save(commit=False)
        instructor.user = user
        if commit:
            instructor.save()
        return instructor



# Instructor login form

from django.contrib.auth.forms import AuthenticationForm

class InstructorLoginForm(AuthenticationForm):
    # You can customize it further, but it's a simple form inheriting from AuthenticationForm
    username = forms.CharField(max_length=150, required=True, help_text="Enter your username.")
    password = forms.CharField(widget=forms.PasswordInput(), required=True, help_text="Enter your password.")



from .models import Course
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'video', 'course_content', 'course_material']
        widgets = {
            'course_content': forms.Textarea(attrs={'class': 'rich-text-editor'}),
        }
