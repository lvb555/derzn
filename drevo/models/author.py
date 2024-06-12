from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models

from drevo.common.file_storage import ASCIIFileSystemStorage
from users.models import User


class Author(models.Model):
    """
    Класс для описания авторов
    """
    title = 'Автор'
    name = models.CharField(max_length=128,
                            verbose_name='Имя')
    user_author = models.ForeignKey(User,
                               on_delete=models.PROTECT,
                               verbose_name='Пользователь',
                               related_name='users',
                               blank=True,
                               null=True
                               )
    subscribers = models.ManyToManyField('users.User', blank=True)
    info = models.TextField(max_length=2048,
                            blank=True,
                            null=True,
                            verbose_name='Сведения об авторе'
                            )
    photo = models.ImageField(upload_to='photos/authors/',
                              verbose_name='Фото',
                              blank=True,
                              null=True,
                              storage=ASCIIFileSystemStorage()
                              )
    atype = models.ForeignKey('AuthorType',
                              on_delete=models.PROTECT,
                              verbose_name='Вид автора',
                              blank=True,
                              null=True
                              )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата и время редактирования',
                                      )

    objects = models.Manager()

    def __str__(self):
        return self.name

    @classmethod
    def get_author_by_user(cls, user: User) -> 'Author':
        """Возвращает запись автора по пользователю
            Если их много (это баг), то возвращает первую
            Если нет автора, то создает запись и возвращает ее"""
        try:
            author = cls.objects.get(user_author=user)

        except ObjectDoesNotExist:
            author = cls.objects.create(user_author=user, name=user.get_full_name())

        except MultipleObjectsReturned:
            author = cls.objects.filter(user_author=user).first()

        return author

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
