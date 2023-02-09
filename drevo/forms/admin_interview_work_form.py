from django import forms
from ..models import InterviewAnswerExpertProposal


class InterviewAnswerExpertProposalForms(forms.ModelForm):
    """
        Форма для раздела "Работа администратора по вопросу"
    """
    class Meta:
        model = InterviewAnswerExpertProposal
        fields = ['admin_comment', 'status']
        widgets = {

            'admin_comment': forms.Textarea(
                attrs={'class': 'form-control', 'style': 'overflow-y: scroll; height: 125px; width: 250px'}
            ),
            'status': forms.Select(attrs={'class': 'form-control', 'style': 'width: 200px'})
        }

    def __init__(self, *args, **kwargs):
        super(InterviewAnswerExpertProposalForms, self).__init__(*args, **kwargs)
        self.fields['status'].choices = [
            (None, '------'),
            ("APPRVE", "Принят"),
            ("REJECT", "Не принят"),
        ]
        self.old_status = self.instance.status
        self.old_comment = self.instance.admin_comment
        if self.instance.status == 'APPRVE':
            self.old_answer = self.instance.new_answer
        else:
            self.old_answer = self.instance.answer
        if self.instance.status:
            self.fields['admin_comment'].widget.attrs['disabled'] = 'true'
            self.fields['status'].widget.attrs['disabled'] = 'true'
            if self.instance.status == 'ANSDPL':
                self.fields['status'].choices += [("ANSDPL", "Дубль. отв.")]
            elif self.instance.status == 'RESDPL':
                self.fields['status'].choices += [("RESDPL", "Дубль. предл.")]
