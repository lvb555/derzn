from django.db import models


class RelationshipTzTr(models.Model):
    """
        Взаимосвязи видов знаний и связей
    """
    base_tz = models.ForeignKey(
        verbose_name='Вид базового знания',
        to='drevo.Tz',
        on_delete=models.CASCADE,
        related_name='base_relationship'
    )
    rel_type = models.ForeignKey(
        verbose_name='Вид связи',
        to='drevo.Tr',
        on_delete=models.CASCADE,
        related_name='relationship'
    )
    rel_tz = models.ForeignKey(
        verbose_name='Вид связанного знания',
        to='drevo.Tz',
        on_delete=models.CASCADE,
        related_name='related_relationship'
    )

    class Meta:
        verbose_name = 'Взаимосвязи видов знаний и связей'
        verbose_name_plural = 'Взаимосвязь вида знания и связи'
