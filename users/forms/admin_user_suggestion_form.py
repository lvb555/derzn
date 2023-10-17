from django import forms
from ..models import UserSuggection

class UserSuggestionAdminForm(forms.ModelForm):
    class Meta:
        model = UserSuggection
        fields = ["parent_knowlege", "name", "user", "suggestions_type", "expert", "is_approve", "check_date"]
        widgets = {
            "name": forms.Textarea(attrs={"cols": 40, "rows": 10}),
        }