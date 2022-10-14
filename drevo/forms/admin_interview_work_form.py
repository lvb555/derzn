from django import forms
from django.db.models import Q
from ..models import InterviewAnswerExpertProposal
from ..models import Znanie


class InterviewAnswerExpertProposalForms(forms.ModelForm):
    """
        Форма для раздела "Работа администратора по вопросу"
    """
    class Meta:
        model = InterviewAnswerExpertProposal
        fields = ['new_answer', 'admin_comment', 'status']
        widgets = {
            'new_answer': forms.Select(attrs={'class': 'form-controls'}),
            'admin_comment': forms.Textarea(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(InterviewAnswerExpertProposalForms, self).__init__(*args, **kwargs)
        answers = Znanie.objects.select_related('tz').filter(
            Q(tz__name='Ответ') | Q(tz__name='Тезис')
        ).values('pk', 'name').all()
        if not self.instance.new_answer:
            self.fields['new_answer'].initial = '------'
        self.fields['new_answer'].choices = [('', '------')] + \
                                            [(elm.get('pk'), f"{elm.get('name')[:50]}...") for elm in answers]
        if self.instance.status == 'APPRVE':
            self.fields['new_answer'].widget.attrs['class'] += ' text-danger'

        self.old_status = self.instance.status
        self.old_comment = self.instance.admin_comment
        self.old_answer = self.instance.new_answer
