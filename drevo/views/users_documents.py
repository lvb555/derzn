from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from drevo.forms.users_documents import UsersDocumentsForm
from drevo.models.users_documents import UsersDocuments
from ..models import Znanie


class CreateDocumentView(TemplateView):
    """
    Выводит страницу для создания документа по шаблону.
    """

    template_name = 'drevo/create_document.html'

    def get(self, request, pk, **kwargs):
        """
        Отображает форму для создания документа.
        """

        context = super().get_context_data(**kwargs)

        document_form = UsersDocumentsForm()
        root_name = Znanie.objects.get(pk=pk).name

        context.update({"root_document": root_name,
                        "document_form": document_form})

        return render(request, self.template_name, context=context)
    
    def post(self, request, pk, **kwargs):
        """
        Обрабатывает вводные данные из формы для записи в БД.
        """
        
        form = UsersDocumentsForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            content = form.cleaned_data["content"]
            root_document = Znanie.objects.get(pk=pk)

            UsersDocuments.objects.create(root_document=root_document,
                                          name=name,
                                          content=content,
                                          owner=request.user)
            
        return redirect("users:my_documents")
    

class ChangeDocumentView(TemplateView):
    """
    Выводит страницу для редактирования документа по шаблону.
    """

    template_name = 'drevo/change_document.html'

    def get(self, request, pk, **kwargs):
        """
        Отображает форму для создания документа.
        """

        context = super().get_context_data(**kwargs)
        document = UsersDocuments.objects.get(pk=pk)

        document_form = UsersDocumentsForm(instance=document)
        root_name = document.root_document

        context.update({"root_document": root_name,
                        "document_form": document_form})

        return render(request, self.template_name, context=context)
    
    def post(self, request, pk, **kwargs):
        """
        Обрабатывает вводные данные из формы для записи в БД.
        """

        document = UsersDocuments.objects.get(pk=pk)
        form = UsersDocumentsForm(request.POST, instance=document)

        if form.is_valid():
            name = form.cleaned_data["name"]
            content = form.cleaned_data["content"]

            document.name = name
            document.content = content
            document.save()
            
        return redirect("users:my_documents")


class DeleteDocumentView(TemplateView):
    """
    Представление удаления пользовательского документа.
    """

    template_name = "users/my_documents.html"

    def get(self, request, pk, **kwargs):
        """
        Обрабатывает удаление документа по pk.
        """

        document = UsersDocuments.objects.get(pk=pk)
        document.delete()

        return redirect("users:my_documents")
