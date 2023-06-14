from django.views.generic import TemplateView

class PrivacyPolicyView(TemplateView):
    template_name = 'drevo/privacy_policy.html'