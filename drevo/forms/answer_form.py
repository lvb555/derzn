from django import forms


class FormAnswer(forms.Form):
    answer = forms.CharField(label="Answer", widget=forms.Textarea)
    file = forms.FileField()