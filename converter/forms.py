from django import forms

class uploadPDFForm(forms.Form):
    pdf_file = forms.FileField(label="select a PDF File")