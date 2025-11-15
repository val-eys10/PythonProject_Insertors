from django import forms
from .models import FitnessData

class FitnessDataForm(forms.ModelForm):
    class Meta:
        model = FitnessData
        fields = ['weight', 'height', 'steps', 'calories_burned']
        labels = {
            'weight': 'Weight (kg)',
            'height': 'Height (m)',
        }