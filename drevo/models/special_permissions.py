from django.db import models
from users.models import User
from drevo.models.category import Category


class SpecialPermissions(models.Model):
    """
        Класс с описанием компетенцций и особых прав экспертов
    """
    title = 'Вид "Эксперта"'
    expert = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Эксперт',
        related_name='expert'
    )
    categories = models.ManyToManyField(
        Category,
        related_name='category_list',
        verbose_name='Компетенции эксперта'
    )
    editor = models.BooleanField(
        verbose_name='Редактор',
        default=False
    )
    admin_competencies = models.ManyToManyField(
        verbose_name='Компетенции руководителя',
        to=Category,
        related_name='special_permissions'
    )

    def __str__(self):
        return f'{self.expert}'

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для того, чтобы у пользователя установить флаг is_expert
        """
        if not self.pk:
            user = User.objects.get(id=self.expert.id)
            user.is_expert = True
            user.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Особые права'
        verbose_name_plural = 'Особые права'
