from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.urls import reverse
from mptt.models import TreeForeignKey
from users.models import User

from ..managers import ZManager
from drevo.common import variables
from .category import Category
from .knowledge_grade_scale import KnowledgeGradeScale
from .knowledge_rating import ZnRating
from .relation_type import Tr
from .relation import Relation


class Znanie(models.Model):
    """
    Класс для описания сущности 'Знание'
    """
    title = 'Знание'
    name = models.CharField(
        max_length=255,
        verbose_name='Тема',
        unique=True
    )
    category = TreeForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name='Категория',
        null=True,
        blank=True,
        limit_choices_to={'is_published': True}
    )
    tz = models.ForeignKey(
        'Tz',
        on_delete=models.PROTECT,
        verbose_name='Вид знания'
    )
    content = models.TextField(
        max_length=2048,
        blank=True,
        null=True,
        verbose_name='Содержание'
    )
    href = models.URLField(
        max_length=256,
        verbose_name='Источник',
        help_text='укажите www-адрес источника',
        null=True,
        blank=True)
    source_com = models.CharField(
        max_length=256,
        verbose_name='Комментарий к источнику',
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        'Author',
        on_delete=models.PROTECT,
        verbose_name='Автор',
        help_text='укажите автора',
        null=True,
        blank=True
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата и время редактирования',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        editable=False,
        verbose_name='Пользователь'
    )
    expert = models.ForeignKey(User,
                               on_delete=models.PROTECT,
                               null=True,
                               blank=True,
                               related_name='knowledge_expert',
                               verbose_name='Эксперт'
                               )
    redactor = models.ForeignKey(User,
                                 on_delete=models.PROTECT,
                                 null=True,
                                 blank=True,
                                 related_name='redactor',
                                 verbose_name='Редактор'
                                 )
    director = models.ForeignKey(User,
                                 on_delete=models.PROTECT,
                                 null=True,
                                 blank=True,
                                 related_name='director',
                                 verbose_name='Руководитель')
    order = models.IntegerField(
        verbose_name='Порядок',
        help_text='укажите порядковый номер',
        null=True,
        blank=True
    )

    is_published = models.BooleanField(
        default=False,
        verbose_name='Опубликовано?'
    )
    labels = models.ManyToManyField(
        'Label',
        verbose_name='Метки',
        blank=True
    )
    is_send = models.BooleanField(
        verbose_name='Пересылать',
        default=True
    )
    show_link = models.BooleanField(
        verbose_name='Отображать как ссылку?',
        default=True,
    )
    notification = models.BooleanField(
        default=False,
        verbose_name='Уведомления'
    )
    several_works = models.BooleanField(
        default=False,
        verbose_name='Несколько работ'
    )

    # Для обработки записей (сортировка, фильтрация) вызывается собственный Manager,
    # в котором уже установлена фильтрация по is_published и сортировка
    objects = models.Manager()
    published = ZManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('zdetail', kwargs={"pk": self.pk})

    def voting(self, user, value):
        rating_obj = self.znrating_set.filter(user=user).first()

        if rating_obj:
            if value == rating_obj.value:
                rating_obj.value = ZnRating.BLANK
            else:
                rating_obj.value = value

            rating_obj.save()
        else:
            ZnRating.objects.create(znanie=self, user=user, value=value)

    def get_users_vote(self, user):
        rating_obj = self.znrating_set.filter(user=user).first()

        if rating_obj:
            if rating_obj.value in (ZnRating.LIKE, ZnRating.DISLIKE):
                return rating_obj.value

        return None

    def get_likes_count(self):
        return self.znrating_set.filter(value=ZnRating.LIKE).count()

    def get_dislikes_count(self):
        return self.znrating_set.filter(value=ZnRating.DISLIKE).count()

    def get_comments_count(self):
        return self.comments.filter(parent=None).count()

    def get_table_object(self):
        if self.tz.name != 'Таблица':
            return None

        row_type_name = 'Строка'
        col_type_name = 'Столбец'
        value_type_name = 'Значение'

        row_type = Tr.objects.get(name=row_type_name)
        col_type = Tr.objects.get(name=col_type_name)
        value_type = Tr.objects.get(name=value_type_name)

        rows = sorted(
            self.base.filter(tr=row_type).select_related('rz'),
            key=lambda x: x.rz.order if x.rz.order else 0,
            reverse=True
        )
        cols = sorted(
            self.base.filter(tr=col_type).select_related('rz'),
            key=lambda x: x.rz.order if x.rz.order else 0,
            reverse=True
        )

        # если нет строк и/или колонок - выходим
        if not all([rows, cols]):
            return None

        target_rows = rows
        target_cols = cols

        if rows[0].rz.tz.is_group:
            target_rows = rows[0].get_grouped_relations()
        if cols[0].rz.tz.is_group:
            target_cols = cols[0].get_grouped_relations()

        target_rows = [row.rz for row in target_rows]
        target_cols = [col.rz for col in target_cols]

        values = self.base.filter(tr=value_type).values_list('rz', flat=True)

        # отбираем связи где базовое знание из списка values, а зависимое - это строка или столбец
        # причем строки и столбцы из списка
        values_positions = Relation.objects.filter(Q(bz__in=values) & (
                (Q(tr=row_type) & Q(rz__in=target_rows)) |
                (Q(tr=col_type) & Q(rz__in=target_cols))
        )).order_by('bz')

        # делаем группировку значения и его координат в словаре
        # в идеале должно быть по одному значению строки и столбца на значение
        # но могут быть всякие баги....
        positions = {}
        for record in values_positions:
            current_pos = positions.setdefault(record.bz, {'cols': [], 'rows': []})
            if record.tr == col_type:
                current_pos['cols'].append(record.rz)

            elif record.tr == row_type:
                current_pos['rows'].append(record.rz)

            else:
                raise ValueError('Invalid relation type')

        # матрица таблицы размером кол-во рядов х кол-во колонок
        matrix = [[None]*len(target_cols) for _ in range(len(target_rows))]

        for value, pos in positions.items():
            if len(pos['cols']) == 1 and (len(pos['rows']) == 1):
                col = pos['cols'][0]
                row = pos['rows'][0]
                row_i = target_rows.index(row)  # не оптимально, но список должен быть небольшой
                col_j = target_cols.index(col)
                matrix[row_i][col_j] = value
            else:
                # надо бы ошибку сгенерировать
                pass

        table_object = {
            'rows': rows,
            'cols': cols,
            'values': matrix,
        }
        return table_object

    def get_users_grade(self, user: User):
        """
        Оценка пользователя user.
        По умолчанию - Нет оценки
        """

        queryset = self.grades.filter(user=user)
        if queryset.exists():
            return queryset.first().grade.get_base_grade()
        return KnowledgeGradeScale.objects.get(name='Нет оценки').get_base_grade()

    def get_common_grades(self, request):
        """
        Расчёт общей оценки знания.
        Возвращает числовое значение общей оценки и
        числовое значение оценки доказательной базы (ОДБ).
        """

        variant = request.GET.get('variant')
        if variant and variant.isdigit():
            variant = int(variant)
        else:
            variant = 1

        proof_base_value = self.get_proof_base_grade(request, variant)
        if proof_base_value is not None:
            users_grade = self.get_users_grade(request.user)
            if users_grade is not None:
                common_grade_value = (proof_base_value + users_grade) / 2
            else:
                common_grade_value = None
        else:
            common_grade_value = self.get_users_grade(request.user)

        return common_grade_value, proof_base_value

    def get_proof_base_grade(self, request, variant):
        """
        Возвращает числовое значение оценки доказательной базы
        """

        sum_list = []

        queryset = self.base.filter(
            tr__is_argument=True,
            rz__tz__can_be_rated=True,
        )
        if queryset.exists():
            for relation in queryset:
                grade = relation.get_proof_weight(request, variant)

                if grade:
                    sum_list.append(grade)

        if not sum_list:
            # Если доводов нет, Тогда ОДБ := None
            return None

        # ОДБ := среднее арифметическое Оценок вкладов доводов (ОВД) среди существенных доводов..
        proof_base_value = sum(sum_list) / len(sum_list)

        if proof_base_value < 0:
            # Если ОДБ < 0, тогда ОДБ := 0
            proof_base_value = 0

        return proof_base_value

    @staticmethod
    def get_default_grade():
        """ Возвращает числовое значение оценки по умолчанию """
        return KnowledgeGradeScale.objects.all().first().get_base_grade()

    def get_ancestors_category(self):
        """
        Возвращает TreeQuerySet с категорией и предками категории данного знания
        """
        return self.category.get_ancestors(ascending=False, include_self=True)

    def get_expert(self):
        """
        Возвращает список экспертов по данному знанию
        """
        categories = self.get_ancestors_category()
        expert_list = []
        for category in categories:
            experts = category.get_experts()
            if not experts:
                continue
            for expert in experts:
                expert_list.append(expert.expert)
        return expert_list

    @property
    def get_current_status(self):
        """
        Возвращает текущий статус знания
        """
        return self.knowledge_status.get(Q(knowledge=self) & Q(is_active=True))

    def get_status_history(self):
        """
        Возвращает все статусы текущего знания
        """
        return self.knowledge_status.filter(knowledge=self).select_related()

    def get_status_action(self, user: User):
        """
        Возвращает список кортежей с возможным действием для изменения статуса и новым статусом
        :param user: Экземпляр класса модели пользователя
        """
        if user.is_director:
            return variables.TRANSITIONS_DIRECT[self.get_current_status()]
        elif user.is_redactor:
            return variables.TRANSITIONS_RED[self.get_current_status()]
        elif user.is_expert:
            return variables.TRANSITIONS_EXP[self.get_current_status()]
        else:
            return variables.TRANSITIONS_PUB[self.get_current_status()]

    class Meta:
        verbose_name = 'Знание'
        verbose_name_plural = 'Знания'
        ordering = ('order',)
