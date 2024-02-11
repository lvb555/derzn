from django.forms import ModelForm
from drevo.models.users_documents import UsersDocuments


class UsersDocumentsForm(ModelForm):
    
    class Meta:
        model = UsersDocuments
        fields = ('name', 'content', 'is_complete')
