from django.db import models
from .parameter_categories import ParameterCategories
from users.models import User
from django.apps import apps


class SettingsOptions(models.Model):
    name = models.CharField(
        verbose_name='Название параметра',
        max_length=255
    )
    category = models.ForeignKey(
        verbose_name='Категория',
        to=ParameterCategories,
        on_delete=models.CASCADE,
        related_name='params',
        blank=True,
        null=True
    )
    default_param = models.CharField(
        verbose_name='Значение по умолчанию',
        max_length=255
    )
    admin = models.BooleanField(
        verbose_name='Администратор',
        default=False
    )

    class Meta:
        verbose_name = 'Параметр настроек'
        verbose_name_plural = 'Параметры настроек'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.pk and not self.admin:
            super(SettingsOptions, self).save(*args, **kwargs)
            users = User.objects.all()
            user_params_model = apps.get_model(app_label='drevo', model_name='UserParameters')
            updated_users_settings = [
                user_params_model(user=user, param=self, param_value=self.default_param) for user in users
            ]
            user_params_model.objects.bulk_create(updated_users_settings)
            return
        super(SettingsOptions, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
