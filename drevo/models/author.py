from django.db import models


# from derzn.drevo.models import Znanie


class Author(models.Model):
    """
    Класс для описания авторов
    """
    title = 'Автор'
    name = models.CharField(max_length=128,
                            verbose_name='Имя')
    subscribers = models.ManyToManyField('users.User')
    info = models.TextField(max_length=2048,
                            blank=True,
                            null=True,
                            verbose_name='Сведения об авторе'
                            )
    photo = models.ImageField(upload_to='photos/authors/',
                              verbose_name='Фото',
                              blank=True,
                              null=True
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

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
