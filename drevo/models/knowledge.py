from django.db import models
from mptt.models import TreeForeignKey
from django.urls import reverse
from users.models import User
from ..managers import ZManager
from .category import Category
from .knowledge_rating import ZnRating


class Znanie(models.Model):
    """
    Класс для описания сущности 'Знание'
    """
    title = 'Знание'
    name = models.CharField(max_length=256,
                            verbose_name='Тема',
                            unique=True
                            )
    category = TreeForeignKey(Category,
                              on_delete=models.PROTECT,
                              verbose_name='Категория',
                              null=True,
                              blank=True,
                              limit_choices_to={'is_published': True}
                              )
    tz = models.ForeignKey('Tz',
                           on_delete=models.PROTECT,
                           verbose_name='Вид знания'
                           )
    content = models.TextField(max_length=2048,
                               blank=True,
                               null=True,
                               verbose_name='Содержание'
                               )
    href = models.URLField(max_length=256,
                           verbose_name='Источник',
                           help_text='укажите www-адрес источника',
                           null=True,
                           blank=True)
    source_com = models.CharField(max_length=256,
                                  verbose_name='Комментарий к источнику',
                                  null=True,
                                  blank=True
                                  )
    author = models.ForeignKey('Author',
                               on_delete=models.PROTECT,
                               verbose_name='Автор',
                               help_text='укажите автора',
                               null=True,
                               blank=True
                               )
    date = models.DateField(auto_now_add=True,
                            verbose_name='Дата создания',
                            )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата и время редактирования',
                                      )
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT,
                             editable=False,
                             verbose_name='Пользователь'
                             )
    order = models.IntegerField(verbose_name='Порядок',
                                help_text='укажите порядковый номер',
                                null=True,
                                blank=True
                                )

    is_published = models.BooleanField(default=False,
                                       verbose_name='Опубликовано?'
                                       )
    labels = models.ManyToManyField('Label',
                                    verbose_name='Метки',
                                    blank=True
                                    )
    # Для обработки записей (сортировка, фильтрация) вызывается собственный Manager,
    # в котором уже установлена фильтрация по is_published и сортировка
    objects = models.Manager()
    published = ZManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('zdetail', kwargs={"pk": self.pk})

    def voting(self, user, value):
        rating_obj = self.znrating_set.filter(user=user).first()
    

        if rating_obj:
            if value == rating_obj.value:
                rating_obj.value = ZnRating.BLANK
            else:
                rating_obj.value = value

            rating_obj.save()
        else:
            ZnRating.objects.create(znanie=self, user=user, value=value)

    def get_users_vote(self, user):
        rating_obj = self.znrating_set.filter(user=user).first()

        if rating_obj:
            if rating_obj.value in (ZnRating.LIKE, ZnRating.DISLIKE):
                return rating_obj.value

        return None

    def get_likes_count(self):
        return self.znrating_set.filter(value=ZnRating.LIKE).count()

    def get_dislikes_count(self):
        return self.znrating_set.filter(value=ZnRating.DISLIKE).count()

    def get_comments_count(self):
        return self.comments.filter(parent=None).count()

    class Meta:
        verbose_name = 'Знание'
        verbose_name_plural = 'Знания'
        ordering = ('order',)
