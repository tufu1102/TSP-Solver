#forms.py
from django import forms

class TSPForm(forms.Form):
    INPUT_CHOICES = [
        ('text', 'Text Input'),
        ('file', 'File Input (CSV/Text)'),
        ('map', 'Integrated Map Input'),
        ('voice', 'Voice Input'),
    ]

    input_type = forms.ChoiceField(choices=INPUT_CHOICES, label='Input Type', required=True)
    text_input = forms.CharField(label='Text Input', required=False, widget=forms.Textarea(attrs={'rows': 5, 'placeholder': "Type addresses separated in multiple lines"}))
    csv_file = forms.FileField(label='CSV File', required=False)
    sheet_name = forms.CharField(label='Sheet Name', required=False)
    map_input = forms.CharField(label='Map Input', required=False)  # Assuming map input is collected as text (coordinates)
    voice_input = forms.CharField(label='Voice Input', required=False)


