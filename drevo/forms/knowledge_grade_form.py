from django import forms
from drevo.models.knowledge_grade import KnowledgeGrade


class KnowledgeGradeForm(forms.ModelForm):
    user = forms.IntegerField(widget=forms.HiddenInput())
    knowledge = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = KnowledgeGrade
        fields = ('user', 'knowledge', 'grade',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(args)
        print(kwargs)

    def is_valid(self):
        print(self.knowledge)