from django.db import models


class SubAnswers(models.Model):
    """
    Данная модель хранит подответы для знаний (ответов на вопрос интервью),
    которые были созданы на основе предложений экспертов
    """
    expert = models.ForeignKey(
        verbose_name='Эксперт',
        to='users.User',
        on_delete=models.CASCADE,
        related_name='sub_answers'
    )
    question = models.ForeignKey(
        verbose_name='Вопрос',
        to='drevo.Znanie',
        on_delete=models.CASCADE,
        related_name='quest_sub_answers'
    )
    answer = models.ForeignKey(
        verbose_name='Ответ',
        to='drevo.Znanie',
        on_delete=models.CASCADE,
        related_name='answ_sub_answers'
    )
    sub_answer = models.TextField(
        verbose_name='Подответ'
    )

    class Meta:
        verbose_name = 'Подответ'
        verbose_name_plural = 'Подответы'

    def __str__(self):
        return f'SubAnswer #{self.pk}: {self.expert}'
