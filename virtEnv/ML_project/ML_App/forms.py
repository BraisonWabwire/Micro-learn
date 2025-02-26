from django import forms
from django.forms.widgets import PasswordInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Instructor, Course, Profile,Assignment, Question, Choice


class SignupForm(UserCreationForm):
    is_instructor = forms.BooleanField(required=False, label='Are you an instructor?')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update password1 and password2 fields' widgets for custom placeholders
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'is_instructor']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Firstname'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Lastname'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            # The placeholders for password fields are set in the __init__ method now
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(user=user, is_instructor=self.cleaned_data['is_instructor'])
            if self.cleaned_data['is_instructor']:
                Instructor.objects.create(user=user, name=f"{user.first_name} {user.last_name}", email=user.email)
        return user

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
            Profile.objects.create(user=user, is_instructor=True)
        return instructor

class InstructorLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True, help_text="Enter your username.")
    password = forms.CharField(widget=forms.PasswordInput(), required=True, help_text="Enter your password.")

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'video', 'course_content', 'course_material']
        widgets = {
            'course_content': forms.Textarea(attrs={'class': 'rich-text-editor'}),
        }



# Handling assignment
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'course']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Enter assignment title'}),
            'description': forms.Textarea(attrs={'class': 'custom-textarea', 'rows': 3, 'placeholder': 'Describe the assignment'}),
            'course': forms.Select(attrs={'class': 'custom-select'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Enter question'}),
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Enter choice text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'video', 'course_content', 'course_material']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder':'Write a 3-4 words title'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Write a short 10-word description.'
            })
        }
