from django.views.generic import TemplateView
from ..models.chapter import ChapterDescriptions


class AboutView(TemplateView):
    """
    Выводит страницу описания проекта
    """
    template_name = 'drevo/about_proj.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Передает данные в шаблон
        """
        context = super().get_context_data(**kwargs)
        chapters = (ChapterDescriptions.objects
                    .all()
                    .order_by("order")
                    )
        
        preamble = chapters.first()
        chapters_list = chapters[1:]

        context["preamble"] = preamble
        context["chapters"] = chapters_list

        return context