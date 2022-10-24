from django.shortcuts import Http404, get_object_or_404
from django.views.generic import TemplateView
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale


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

        Grades = KnowledgeGrade.objects.filter(knowledge_id=kwargs['pk'])

        gender_grades = {}
        amount_all_grades = Grades.count()
        amount_all_grades_man = Grades.filter(user__profile__gender="M").count()
        amount_all_grades_female = Grades.filter(user__profile__gender="F").count()

        for GradeScale in KnowledgeGradeScale.objects.all():
            amount_grade = Grades.filter(grade=GradeScale.id).count()            
            amount_man_grade = Grades.filter(grade=GradeScale.id, user__profile__gender="M").count()                          
            amount_female_grade = Grades.filter(grade=GradeScale.id, user__profile__gender="F").count()

            try:
                percent_grade = round(amount_grade / amount_all_grades * 100, 1)
            except ZeroDivisionError:
                percent_grade = 0

            try:
                percent_man_grade = round(amount_man_grade / amount_all_grades_man * 100, 1)
            except ZeroDivisionError:
                percent_man_grade = 0  
            
            try:
                percent_female_grade = round(amount_female_grade / amount_all_grades_female)
            except ZeroDivisionError:
                percent_female_grade = 0

            gender_grades[GradeScale] = [
                amount_grade, percent_grade,
                amount_man_grade, percent_man_grade,
                amount_female_grade, percent_female_grade]

        gender_grades["Всего:"] = [
            amount_all_grades, 100,
            amount_all_grades_man, 100,
            amount_all_grades_female, 100]

        context['gender_grades'] = gender_grades

        return context
