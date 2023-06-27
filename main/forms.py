from django import forms
from .models import Hand
from mapbox_location_field.models import LocationField
from location_field.forms.plain import PlainLocationField


class HandForm(forms.ModelForm):
    class Meta:
        model = Hand
        fields = (
            "title",
            "description",
            "request_date",
            "request_start_time",
            "request_end_time",
            "request_price",
        )

        widgets = {
            # https://stackoverflow.com/questions/22846048/django-form-as-p-datefield-not-showing-input-type-as-date
            "description": forms.Textarea(),
            "request_date": forms.DateInput(attrs={"type": "date"}),
            "request_start_time": forms.DateInput(attrs={"type": "time"}),
            "request_end_time": forms.DateInput(attrs={"type": "time"}),
        }
