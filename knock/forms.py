# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from knock.models import Knock, Profile


class KnockForm(forms.ModelForm):
    class Meta:
        model = Knock
        fields = (
            'title',
            'description',
            'category',
            'request_date',
            'request_start_time',
            'request_end_time',
            'request_price',
        )

        widgets = {
            # https://stackoverflow.com/questions/22846048/django-form-as-p-datefield-not-showing-input-type-as-date
            'description': forms.Textarea(),
            'request_date': forms.DateInput(attrs={'type': 'date'}),
            'request_start_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'pattern': r'[0-9]{2}:[0-9]{2}'}),
            'request_end_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'pattern': r'[0-9]{2}:[0-9]{2}'}),
        }


class UserRegisterForm(UserCreationForm):
    # pylint: disable=too-many-ancestors

    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']

# Create a UserUpdateForm to update a username and email


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name']

# Create a ProfileUpdateForm to update image.


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['gender', 'image']
