from django import forms


class SelectWithInput(forms.Select):
    template_name = 'drevo/forms/select.html'
    option_template_name = 'drevo/forms/select_option.html'
