from tabnanny import verbose
from django.db import models
from users.models import User
from drevo.models import Znanie


class QuizResult(models.Model):
    """
    Таблица для хранения результатов теста
    """
    quiz = models.ForeignKey(Znanie, verbose_name='Тест', related_name='passed_quiz', on_delete=models.CASCADE)
    question = models.ForeignKey(Znanie, verbose_name='Вопрос', related_name='questions_in_quiz', on_delete=models.CASCADE)
    answer = models.ForeignKey(Znanie, verbose_name='Ответ', related_name='answers_in_quiz', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Тестируемый', related_name='quiz_results', on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время решения')

    class Meta:
        verbose_name = 'Результаты теста'
        verbose_name_plural = 'Результаты тестов'

    def __str__(self):
        return f'{self.user} - {self.quiz}({self.date_time:%d.%m.%Y})'
