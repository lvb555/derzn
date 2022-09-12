from django.db import models
from users.models import User
from drevo.models.category import Category


class CategoryExpert(models.Model):
    """
    Класс для описания привязки экспертов к категориям
    """
    title = 'Вид "Эксперта"'
    expert = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Эксперт',
                               related_name='expert'
                               )
    categories = models.ManyToManyField(Category,
                                        related_name='category_list',
                                        verbose_name='Список категорий'
                                        )

    def __str__(self):
        return f'{self.expert}'

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для того, чтобы у пользователя установить флаг is_expert
        """
        user = User.objects.get(id=self.expert.id)
        user.is_expert = True
        user.save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Эксперта'
        verbose_name_plural = 'Эксперты'
