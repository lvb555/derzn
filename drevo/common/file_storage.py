from slugify import slugify
from django.core.files.storage import FileSystemStorage

class ASCIIFileSystemStorage(FileSystemStorage):
    """
    Для автоматической транслитерации всех загружаемых файлов
    """
    def get_valid_name(self, name):
        name_parts = name.split('.')
        name = slugify(name_parts[0])
        name = '{}.{}'.format(name, name_parts[-1])
        return super(ASCIIFileSystemStorage, self).get_valid_name(name)