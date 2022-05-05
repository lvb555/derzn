from django import forms


class SelectWithInputMulti(forms.Select):
    template_name = 'drevo/forms/select_multi.html'
    option_template_name = 'drevo/forms/select_option.html'
