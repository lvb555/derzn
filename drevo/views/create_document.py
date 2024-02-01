from django.views.generic import TemplateView
from django.shortcuts import render

from drevo.forms.users_documents import UsersDocumentsForm


class CreateDocumentView(TemplateView):
    """
    Выводит страницу для создания документа по шаблону
    """

    template_name = 'drevo/create_document.html'

    def get(self, request, pk, **kwargs):
        """
        Отображает форму для создания документа
        """

        context = super().get_context_data(**kwargs)

        document_form = UsersDocumentsForm()

        context.update({'doc_user': self.request.user,
                        'doc_pk': self.kwargs.get('pk'),
                        'document_form': document_form})

        return render(request, self.template_name, context=context)
