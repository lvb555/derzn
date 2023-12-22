from django import forms
from drevo.models.knowledge_kind import Tz

class CtrlOnlySelectMultiple(forms.SelectMultiple):
    class Media:
        js = ['admin/js/admin/tz_multiple_selecting.js']
        css = {
            'all': ['admin/css/admin/tz_multiple_selecting.css']
        }

class AdminKnowledgeKindForm(forms.ModelForm):
    class Meta:
        model = Tz
        fields = [
            "name",
            "order",
            "is_systemic",
            "is_group",
            "can_be_rated",
            "is_send",
            "is_author_required",
            "is_href_required",
            "available_suggestion_types"
        ]
        widgets = {
            "available_suggestion_types": CtrlOnlySelectMultiple()
        }
