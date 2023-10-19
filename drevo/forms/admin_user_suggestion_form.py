from django import forms
from drevo.models.suggestion import Suggestion

class AdminSuggestionUserForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ["parent_knowlege", "name", "user", "suggestions_type", "expert", "is_approve", "check_date"]
        widgets = {
            "name": forms.Textarea(attrs={"cols": 40, "rows": 10}),
        }