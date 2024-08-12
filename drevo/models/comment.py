from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse



User = get_user_model()


class Comment(models.Model):
    CONTENT_MAX_LENGTH = 2000
    COMMENTS_PER_PAGE = 3

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='Автор комментария',
        null=True
    )
    parent = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        default=None,
        on_delete=models.CASCADE,
        verbose_name='Родительский комментарий',
        related_name='answers',
    )
    znanie = models.ForeignKey(
        'Znanie',
        on_delete=models.CASCADE,
        verbose_name='Знание',
        related_name='comments',
    )
    content = models.TextField(
        max_length=2000,
        blank=True,
        verbose_name='Тело комментария',
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликован'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата и время изменения',
    )
    objects = models.Manager()
    likes = models.ManyToManyField(User, related_name="comments_like", blank=True)
    dislikes = models.ManyToManyField(User, related_name="comments_dislike", blank=True)

    def number_of_likes(self):
            return self.likes.count()

    def number_of_dislikes(self):
            return self.dislikes.count()

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

