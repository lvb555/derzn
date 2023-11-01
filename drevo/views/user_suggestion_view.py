from django.views.generic import TemplateView
from ..models.knowledge import Znanie
from ..models.suggestion import Suggestion
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Model


class UserSuggestionView(TemplateView):
    template_name = 'drevo/suggestions.html'
    context_object_name = 'context'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        parent_knowlege = context['pk']

        # результат отправки формы
        context['knowledge'] = Znanie.objects.get(id=parent_knowlege)

        # предложения, отправленные пользователем
        if user.is_authenticated:
            context['user_suggestions'] = Suggestion.objects.filter(
                user=user,
                parent_knowlege=parent_knowlege).order_by('-suggestions_type', '-create_date')

        return context

    def post(self, request, *args, **kwargs):
        # получение родительского знания
        try:
            knowledge = Znanie.objects.get(pk=int(request.POST['parent-knowledge-id']))
        except Model.DoesNotExist:
            # переадресация на исходную страницу
            return HttpResponseRedirect(request.get_full_path(),
                                        content='Не определено родительское знание',
                                        content_type='text/plain')
        # создание предложений, вписанных пользователем в форму
        for t in knowledge.tz.available_suggestion_types.all():
            for sugg in request.POST.getlist(f'field-of-type-{t.pk}'):

                simplified_string = sugg
                for char in ['\n', '\r', '\t', ' ']:
                    simplified_string = simplified_string.replace(char, '')

                if len(simplified_string) > 0 and len(sugg) < 256:
                    Suggestion.objects.create(
                        parent_knowlege=knowledge,
                        name=sugg,
                        suggestions_type=t,
                        user=self.request.user
                    )
        # переадресация на страницу с предложениями пользователя
        return HttpResponseRedirect(reverse('create-suggestion', args=[knowledge.pk]))
