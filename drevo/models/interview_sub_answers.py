from django.core.exceptions import ValidationError
from django.db import models

from . import Tr
from .knowledge import Znanie
from .relation import Relation


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

    def clean(self):
        if not self._is_question(self.question):
            raise ValidationError(f'Знание "{self.question}" не является вопросом')
        if not self._is_answer(self.answer):
            raise ValidationError(f'Знание "{self.answer}" не является ответом')

    @staticmethod
    def _is_question(knowledge: Znanie) -> bool:
        """
            Проверка на то, что знание является вопросом
            :param knowledge:
            :return:
        """
        queryset = Relation.objects.filter(bz_id=knowledge.pk, tr_id=Tr.objects.get(name="Ответ [ы]").pk)
        return True if queryset.exists() else False

    @staticmethod
    def _is_answer(knowledge: Znanie) -> bool:
        """
            Проверка на то, что знание является ответом
            :param knowledge:
            :return:
        """
        queryset = Relation.objects.filter(rz_id=knowledge.pk, tr_id=Tr.objects.get(name="Ответ [ы]").pk)
        return True if queryset.exists() else False

    def __str__(self):
        return f'SubAnswer #{self.pk}: {self.expert}'
