from django import forms
from mptt.forms import TreeNodeMultipleChoiceField
from drevo.models.category import Category


class CtegoryExpertForm(forms.ModelForm):
    category = TreeNodeMultipleChoiceField(queryset=Category.objects.all())
    admin_competencies = TreeNodeMultipleChoiceField(queryset=Category.objects.all(), required=False)
