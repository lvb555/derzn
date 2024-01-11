from django.db import models
from .suggestion_type import SuggestionKind


class Suggestion(models.Model):
    parent_knowlege = models.ForeignKey(
        to='drevo.Znanie',
        on_delete=models.DO_NOTHING,
        verbose_name='Знание')
    name = models.CharField(
        max_length=255,
        verbose_name='Предложение')
    user = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='suggestions',
        verbose_name='Пользователь')
    suggestions_type = models.ForeignKey(
        to='drevo.SuggestionKind',
        on_delete=models.CASCADE,
        verbose_name='Вид предложения')
    expert = models.ForeignKey(
        to='users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='checked_suggestions',
        verbose_name='Эксперт')
    is_approve = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        verbose_name='Результат проверки')
    check_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата проверки')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Suggestion from {self.user}'

    class Meta:
        verbose_name = 'Предложение пользователя'
        verbose_name_plural = 'Предложения пользователей'