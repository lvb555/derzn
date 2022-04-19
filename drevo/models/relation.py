from django.db import models
from users.models import User

class Relation(models.Model):
    """
    Класс для связи Знание-Знание
    """
    title = 'Связь'
    # связанное знание
    bz = models.ForeignKey('Znanie',
                           on_delete=models.PROTECT,
                           verbose_name='Базовое знание',
                           help_text='укажите базовое знание',
                           related_name='base'
                           )
    tr = models.ForeignKey('Tr',
                           on_delete=models.PROTECT,
                           verbose_name='Вид связи',
                           help_text='укажите вид связи'
                           )
    rz = models.ForeignKey('Znanie',
                           on_delete=models.PROTECT,
                           verbose_name='Связанное знание',
                           help_text='укажите связанное знание',
                           related_name='related'
                           )
    author = models.ForeignKey('Author',
                               on_delete=models.PROTECT,
                               verbose_name='Автор',
                               help_text='укажите автора'
                               )
    date = models.DateField(auto_now_add=True,
                            verbose_name='Дата создания',
                            )
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT,
                             editable=False,
                             verbose_name='Пользователь'
                             )
    is_published = models.BooleanField(default=False,
                                       verbose_name='Опубликовано?'
                                       )
    objects = models.Manager()

    def __str__(self):
        return f"{self.title} {self.tr.name}"

    class Meta:
        verbose_name = 'Связь'
        verbose_name_plural = 'Связи'
        ordering = ('-date',)
