from django import forms


class FormAnswer(forms.Form):
    answer = forms.CharField(widget=forms.Textarea)
    file = forms.FileField()