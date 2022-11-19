import datetime
import collections 
from django.shortcuts import Http404, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import F
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.age_users_scale import AgeUsersScale


class KnowledgeStatisticFormView(TemplateView):
    template_name = 'drevo/knowledge_grade_statistic.html'

    def get(self, request, *args, **kwargs):
        self.knowledge = get_object_or_404(Znanie, id=kwargs['pk'])
        if self.knowledge.tz.can_be_rated:
            return super().get(request, *args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        knowledge = Znanie.objects.get(id=self.kwargs.get('pk'))
        context['knowledge'] = knowledge

        proof_relations = knowledge.base.filter(
            tr__is_argument=True,
            rz__tz__can_be_rated=True,
        )

        context['proof_relations'] = proof_relations

        grades = KnowledgeGrade.objects.filter(knowledge_id=kwargs['pk'])


        # Блок 1.
        # Формирование контекста для таблицы статистики  разделения по полу
        gender_grades = {}
        # статистика будет только по тем у кого указан пол
        amount_all_grades = grades.exclude(user__profile__gender="U").count()
        amount_all_grades_man = grades.filter(user__profile__gender="M").count()
        amount_all_grades_female = grades.filter(user__profile__gender="F").count()

        def get_percent(numerator: int, denominator: int) -> int:
            try:
                percent = round(numerator / denominator * 100, 1)
            except ZeroDivisionError:
                percent = 0
            return percent

        for GradeScale in KnowledgeGradeScale.objects.all():
            amount_grade = grades.filter(grade=GradeScale.id).exclude(user__profile__gender="U").count()            
            amount_man_grade = grades.filter(grade=GradeScale.id, user__profile__gender="M").count()                          
            amount_female_grade = grades.filter(grade=GradeScale.id, user__profile__gender="F").count()

            percent_grade = get_percent(amount_grade, amount_grade)
            percent_man_grade = get_percent(amount_man_grade, amount_grade)
            percent_female_grade = get_percent(amount_female_grade, amount_grade)

            gender_grades[GradeScale] = [
                amount_grade, percent_grade,
                amount_man_grade, percent_man_grade,
                amount_female_grade, percent_female_grade]

        gender_grades["Всего:"] = [
            amount_all_grades, 100,
            amount_all_grades_man, 100,
            amount_all_grades_female, 100]

        context['gender_grades'] = gender_grades


        # Блок 2.
        # Формирование контекста для разделения по возрасту

        # статистика будет только по тем у кого указана дата рождения
        grades_users_have_birthday = grades.exclude(user__profile__birthday_at=None)
        amount_all_grades = grades_users_have_birthday.count()
        # Высчитываем возраст в днях. age: datetime.timedelta
        now = datetime.date.today()
        Users_with_age = grades_users_have_birthday.annotate(age=((now - F('user__profile__birthday_at'))))

        all_age_segments = AgeUsersScale.objects.all()

        age_grades = {}
        title_age_segment = []
        total_amount_age_grade = collections.defaultdict(lambda: 0)
        total_amount_age_grade["Всего"] = amount_all_grades

        # Перебор по всем оценкам
        for GradeScale in KnowledgeGradeScale.objects.all():
            amount_grade = grades_users_have_birthday.filter(grade=GradeScale.id).count()
            percent_grade = get_percent(amount_grade, amount_grade)
            age_grades[GradeScale] = [[amount_grade, percent_grade]]

            for age_segment in all_age_segments:

                if age_segment not in title_age_segment:
                    title_age_segment.append(age_segment)

                if age_segment.min_age is None:
                    min_age = datetime.timedelta(days=0)
                else:
                    min_age = datetime.timedelta(days=365*age_segment.min_age)
                if age_segment.max_age is None:
                    max_age = datetime.timedelta(days=36500)
                else:
                    max_age = datetime.timedelta(days=365*age_segment.max_age)

                amount_users_in_segment = Users_with_age.filter(age__gte=min_age, age__lt=max_age, grade=GradeScale.id).count()
                percent_users_in_segment = get_percent(amount_users_in_segment, amount_grade)
                age_grades[GradeScale].append([amount_users_in_segment, percent_users_in_segment])

                
                total_amount_age_grade[age_segment] += amount_users_in_segment
                
        # установить None нужно, чтобы передать в шаблон джанго для корректной работы
        total_amount_age_grade.default_factory = None

        context['age_grades'] = age_grades
        context['title_age_segment'] = title_age_segment
        context['total_amount_age_grade'] = total_amount_age_grade

        # Блок 3. Статистика по всем оценкам
        all_grades_statistic = {}

        for GradeScale in KnowledgeGradeScale.objects.all():
            amount_grade = grades.filter(grade=GradeScale.id).count()
            percent_grade = get_percent(amount_grade, grades.count())
            all_grades_statistic[GradeScale] = [amount_grade, percent_grade]

        all_grades_statistic["Всего: "] = [grades.count(), 100]
        context['all_grades_statistic'] = all_grades_statistic
        return context
