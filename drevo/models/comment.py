from django.db import models
from users.models import User


class Comment(models.Model):
    CONTENT_MAX_LENGTH = 2000
    COMMENTS_PER_PAGE = 3

    author = models.ForeignKey(User,
                               on_delete=models.PROTECT,
                               verbose_name='Автор комментария',
                               )
    parent = models.ForeignKey('self',
                               blank=True,
                               null=True,
                               default=None,
                               on_delete=models.PROTECT,
                               verbose_name='Родительский комментарий',
                               related_name='answers',
                               )
    znanie = models.ForeignKey('Znanie',
                               on_delete=models.CASCADE,
                               verbose_name='Знание',
                               related_name='comments',
                               )
    content = models.TextField(max_length=2000,
                               blank=True,
                               verbose_name='Тело комментария',
                               )
    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликован'
                                       )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Дата и время создания',
                                      )
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name='Дата и время изменения',
                                      )
    objects = models.Manager()

    class Meta:
        verbose_name = 'Комментарий знания'
        verbose_name_plural = 'Комментарии знаний'
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.id} - {self.author} - {self.znanie} ({self.created_at:%d.%m.%Y %H:%M})'

    def publish(self):
        self.is_published = True

    def unpublish(self):
        self.is_published = False

    def get_answers(self):
        return self.answers.all()

    @property
    def get_max_length(self):
        return self.CONTENT_MAX_LENGTH
