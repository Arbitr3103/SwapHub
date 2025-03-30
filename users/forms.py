# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from users.services import create_notification

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтвердите пароль'})

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Имя пользователя',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя пользователя'
            }),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'phone', 'avatar']
        labels = {
            'bio': 'О себе',
            'location': 'Местоположение',
            'phone': 'Телефон',
            'avatar': 'Фотография профиля'
        }
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Расскажите о себе'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше местоположение'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш номер телефона'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'phone', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Расскажите о себе',
                'rows': 4
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше местоположение'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер телефона'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
