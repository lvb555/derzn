from django.db import models
from users.models import User
from drevo.models.relation_grade_scale import RelationGradeScale


class Relation(models.Model):
    """
    Класс для связи Знание-Знание
    """
    title = 'Связь'
    # связанное знание
    bz = models.ForeignKey('Znanie',
                           on_delete=models.PROTECT,
                           verbose_name='Базовое знание',
                           help_text='укажите базовое знание',
                           related_name='base'
                           )
    tr = models.ForeignKey('Tr',
                           on_delete=models.PROTECT,
                           verbose_name='Вид связи',
                           help_text='укажите вид связи'
                           )
    rz = models.ForeignKey('Znanie',
                           on_delete=models.PROTECT,
                           verbose_name='Связанное знание',
                           help_text='укажите связанное знание',
                           related_name='related'
                           )
    author = models.ForeignKey('Author',
                               on_delete=models.PROTECT,
                               verbose_name='Автор',
                               help_text='укажите автора'
                               )
    date = models.DateField(auto_now_add=True,
                            verbose_name='Дата создания',
                            )
    user = models.ForeignKey(User,
                             on_delete=models.PROTECT,
                             editable=False,
                             verbose_name='Пользователь'
                             )
    is_published = models.BooleanField(default=False,
                                       verbose_name='Опубликовано?'
                                       )
    objects = models.Manager()

    def __str__(self):
        return f"{self.title} {self.tr.name}"

    def get_grouped_relations(self):
        return list(sorted(
            self.rz.base.all(),
            key=lambda x: x.rz.order if x.rz.order else 0,
            reverse=True
        ))

    class Meta:
        verbose_name = 'Связь'
        verbose_name_plural = 'Связи'
        ordering = ('-date',)

    def get_proof_grade(self, request, variant):
        """ Значение оценки довода (ЗОД) """

        if variant == 2:
            related_knowledge_grade, _ = self.rz.get_common_grades(request)
        else:
            related_knowledge_grade = self.rz.get_users_grade(request.user)

        grades = self.grades.filter(user=request.user)
        if grades.exists():
            relation_grade = grades.first().grade.get_base_grade()
        else:
            relation_grade = RelationGradeScale.objects.first().get_base_grade()

        return related_knowledge_grade * relation_grade if related_knowledge_grade is not None else None

    def get_proof_weight(self, request, variant):
        """ Оценка вклада довода (ОВД) """
        proof_grade = self.get_proof_grade(request, variant)

        if proof_grade:
            # Если ЗОД имеет реальное значение, тогда расчет ОВД проводится по формуле.
            # Если расчета нет, то ОВД равен None.
            return proof_grade * (-2 * self.tr.argument_type + 1)
        else:
            return None

    @staticmethod
    def get_default_grade():
        return RelationGradeScale.objects.all().first().get_base_grade()
