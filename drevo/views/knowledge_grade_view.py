from django.views.generic import TemplateView
from drevo.models import Relation
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.knowledge import Znanie
from drevo.models.relation_grade import RelationGrade
from drevo.models.relation_grade_scale import RelationGradeScale
from django.shortcuts import HttpResponseRedirect, Http404, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib import messages

csrf_protected_method = method_decorator(csrf_protect)


class KnowledgeFormView(TemplateView):
    template_name = 'drevo/knowledge_grade.html'

    def get(self, request, *args, **kwargs):
        knowledge = get_object_or_404(Znanie, id=kwargs.get('pk'))
        if knowledge.tz.can_be_rated:
            return super().get(request, *args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        print(self.request.GET)
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оценка знания'
        knowledge = Znanie.objects.get(id=self.kwargs.get('pk'))
        context['knowledge'] = knowledge
        context['proof_relations'] = knowledge.base.filter(
            tr__is_argument=True,
            rz__tz__can_be_rated=True,
        )
        context['knowledge_scale'] = KnowledgeGradeScale.objects.all()
        context['relation_scale'] = RelationGradeScale.objects.all()

        user = self.request.user
        knowledge = Znanie.objects.get(id=self.kwargs.get('pk'))

        if user.is_authenticated:
            context['selected_base_grade'] = KnowledgeGrade.objects.filter(
                knowledge=knowledge,
                user=user,
            ).first()

        is_general = True
        variant = self.request.GET.get('variant')
        if variant and variant.isdigit() and int(variant) == 1:
            is_general = False

        proof_base_value = KnowledgeGrade.get_proof_base_grade(knowledge, user, is_general=is_general)
        context['proof_base_value'] = proof_base_value
        context['proof_base_grade'] = KnowledgeGradeScale.get_grade_object(proof_base_value)
        common_grade_value = (proof_base_value + knowledge.get_users_grade(user)) / 2
        context['common_grade_value'] = common_grade_value
        context['common_grade'] = KnowledgeGradeScale.get_grade_object(common_grade_value)

        return context

    @csrf_protected_method
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404

        knowledge_pk = kwargs.get('pk')

        base_knowledge_grade = request.POST['base_knowledge_grade']
        user = request.user
        knowledge = Znanie.objects.get(id=knowledge_pk)

        if base_knowledge_grade:
            grade = KnowledgeGradeScale.objects.get(id=base_knowledge_grade)

            KnowledgeGrade.objects.update_or_create(
                knowledge=knowledge,
                user=user,
                defaults={'grade': grade},
            )

        relation_rows = self.request.POST.getlist('relation_row')
        knowledge_grades = self.request.POST.getlist('knowledge_grade')
        relation_grades = self.request.POST.getlist('relation_grade')

        for i, relation_id in enumerate(relation_rows):
            relation = Relation.objects.get(id=relation_id)
            knowledge_grade = KnowledgeGradeScale.objects.get(id=knowledge_grades[i])
            KnowledgeGrade.objects.update_or_create(
                knowledge=relation.rz,
                user=user,
                defaults={'grade': knowledge_grade},
            )
            relation_grade = RelationGradeScale.objects.get(id=relation_grades[i])
            RelationGrade.objects.update_or_create(
                relation=relation,
                user=user,
                defaults={'grade': relation_grade},
            )

        messages.success(request, 'Оценка успешно сохранена')

        return HttpResponseRedirect(self.request.path)
