from django import forms
from ..models import InterviewAnswerExpertProposal, Relation, Tr


class InterviewAnswerExpertProposalForms(forms.ModelForm):
    """
        Форма для раздела "Работа администратора по вопросу"
    """
    class Meta:
        model = InterviewAnswerExpertProposal
        fields = ['answer', 'admin_comment', 'status']
        widgets = {
            'answer': forms.Select(attrs={'class': 'form-controls'}),
            'admin_comment': forms.Textarea(
                attrs={'class': 'form-control', 'style': 'overflow-y: scroll; height: 125px'}
            ),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(InterviewAnswerExpertProposalForms, self).__init__(*args, **kwargs)

        answers = Relation.objects.select_related('rz', 'tr').filter(
            bz=self.instance.question, tr__name='Ответ [ы]'
        ).values('rz__pk', 'rz__name').all()

        if not self.instance.answer:
            self.fields['answer'].initial = '------'
        self.fields['answer'].choices = [(None, '------')] + \
                                        [(elm.get('rz__pk'), f"{elm.get('rz__name')[:50]}...") for elm in answers]
        if self.instance.status == 'APPRVE':
            self.fields['answer'].widget.attrs['class'] += ' text-danger'

        self.old_status = self.instance.status
        self.old_comment = self.instance.admin_comment
        self.old_answer = self.instance.answer
