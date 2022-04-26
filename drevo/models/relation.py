from django.db import models
from users.models import User
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale


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

    def get_proof_grade(self, user: User):
        related_knowledge_grade = self.rz.get_users_grade(user)
        grades = self.grades.filter(user=user)
        if grades.exists():
            relation_grade = grades.first().grade.get_base_grade()
        else:
            relation_grade = KnowledgeGradeScale.objects.first().get_base_grade()
        return related_knowledge_grade * relation_grade

    def get_proof_weight(self, user: User):
        return self.get_proof_grade(user) * (-2 * self.tr.argument_type + 1)
