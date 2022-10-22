from django import forms
from ..models import InterviewAnswerExpertProposal, Relation, Tr
import textwrap


class CustomSelect(forms.Select):
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        if attrs is None:
            attrs = {}
        option_attrs = self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        if selected:
            option_attrs.update(self.checked_attribute)
        if 'id' in option_attrs:
            option_attrs['id'] = self.id_for_label(option_attrs['id'], index)

        if len(label) > 25:
            option_attrs.update({'title': '\n'.join(textwrap.wrap(label, 35))})
            label = f'{label[:25]}...'
        else:
            option_attrs.update({'title': label})

        return {
            'name': name,
            'value': value,
            'label': label,
            'selected': selected,
            'index': index,
            'attrs': option_attrs,
            'type': self.input_type,
            'template_name': self.option_template_name,
        }


class InterviewAnswerExpertProposalForms(forms.ModelForm):
    """
        Форма для раздела "Работа администратора по вопросу"
    """
    class Meta:
        model = InterviewAnswerExpertProposal
        fields = ['new_answer', 'admin_comment', 'status']
        widgets = {
            'new_answer': CustomSelect(
                attrs={
                    'class': 'form-control',
                    'style': 'width: 250px;',
                    'onfocus': 'this.size=5;',
                    'onblur': 'this.size=1;',
                    'onchange': 'this.size=1; this.blur();'
                }),
            'admin_comment': forms.Textarea(
                attrs={'class': 'form-control', 'style': 'overflow-y: scroll; height: 125px; width: 250px'}
            ),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(InterviewAnswerExpertProposalForms, self).__init__(*args, **kwargs)

        answers = Relation.objects.select_related('rz', 'tr').filter(
            bz=self.instance.question, tr__name='Ответ [ы]'
        ).order_by('rz__name', 'rz__order').values('rz__pk', 'rz__name')
        self.fields['status'].choices = [
            (None, '------'),
            ("APPRVE", "Принят"),
            ("REJECT", "Не принят"),
            ("ANSDPL", "Дубль. отв."),
            ("RESDPL", "Дубль. предл."),
        ]
        if not self.instance.new_answer:
            self.fields['new_answer'].initial = '------'
        if self.instance.new_answer:
            self.fields['new_answer'].widget.attrs['title'] = '\n'.join(textwrap.wrap(self.instance.new_answer.name, 35))
        self.fields['new_answer'].choices = [(None, '------')] + \
                                        [(elm.get('rz__pk'), elm.get('rz__name')) for elm in answers]
        if self.instance.status == 'APPRVE':
            self.fields['new_answer'].widget.attrs['class'] += ' text-danger'
        self.old_status = self.instance.status
        self.old_comment = self.instance.admin_comment
        self.old_answer = self.instance.answer
