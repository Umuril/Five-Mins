# -*- coding: utf-8 -*-
from django import forms

from .models import Hand


class HandForm(forms.ModelForm):
    class Meta:
        model = Hand
        fields = (
            'title',
            'description',
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
