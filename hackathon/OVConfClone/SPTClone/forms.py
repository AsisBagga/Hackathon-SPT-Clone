from django import forms
from .models import Spt, Config

class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = '__all__'


class SptForm(forms.ModelForm):
    class Meta:
        model = Spt
        fields = '__all__'
