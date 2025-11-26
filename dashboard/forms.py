from django import forms
from .models import FitnessData

class FitnessDataForm(forms.ModelForm):
    class Meta:
        model = FitnessData
        fields = ['weight', 'height', 'steps', 'calories_burned']
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight (kg)',
                'step': '0.1',
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Height (m)',
                'step': '0.01',
            }),
            'steps': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Steps',
            }),
            'calories_burned': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calories Burned',
            }),
        }
        labels = {
            'weight': 'Weight (kg)',
            'height': 'Height (m)',
            'steps': 'Steps',
            'calories_burned': 'Calories Burned',
        }