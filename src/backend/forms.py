from django import forms
from django.core.exceptions import ValidationError
import os


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)
        _, file_extension = os.path.splitext(data['file'].name)
        if file_extension.lower() != '.wav':
            raise ValidationError("Filetype not allowed")
        if data['file'].size > 10000000:
            raise ValidationError("Max 10MB")
