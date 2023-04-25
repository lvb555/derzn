from django.db import models

class KnowledgeGradeColor(models.Model):
    ANY = False
    AGAINST = True

    KNOWLEDGE_TYPES = (
        (ANY, 'Любые знания'),
        (AGAINST, 'Довод "Против"'),
    )

    hue = models.IntegerField(verbose_name="Оттенок")
    saturation = models.IntegerField(verbose_name="Насыщенность")
    high_light = models.IntegerField(verbose_name="Верхняя яркость")
    low_light = models.IntegerField(verbose_name="Нижняя яркость")
    knowledge_type = models.BooleanField(
        choices=KNOWLEDGE_TYPES,
        default=ANY,
        verbose_name='Тип знания'
    )

    class Meta:
        verbose_name = "Спектр цвета"
        verbose_name_plural = "Спектр цвета оценки знания"
