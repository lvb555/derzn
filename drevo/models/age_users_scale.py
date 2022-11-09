from django.db import models

class AgeUsersScale(models.Model):
  title = 'Возраст'
  min_age = models.PositiveSmallIntegerField(verbose_name='Левая граница возраста', blank=True, null=True)
  max_age = models.PositiveSmallIntegerField(verbose_name='Правая граница возраста', blank=True, null=True)
  
  def __str__(self):
    if self.min_age and self.max_age:
        return f"От {self.min_age} до {self.max_age} лет"
    
    elif self.min_age:
      return f"{self.min_age}+ лет"
    
    elif self.max_age:
      return f"До {self.max_age} лет"

  class Meta:
        verbose_name = 'Границы возраста'
        verbose_name_plural = 'Шкала возраста пользователей'
        ordering = ('min_age',)