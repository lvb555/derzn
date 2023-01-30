import copy

from drevo.utils import get_group_users, get_average_proof_base_and_common_grades
from django.shortcuts import Http404, get_object_or_404
from django.views.generic import TemplateView
from drevo.models.knowledge import Znanie
from drevo.models.age_users_scale import AgeUsersScale


class GroupKnowledgeStatisticsView(TemplateView):
    template_name = 'drevo/group_knowledge_grade_statistics.html'

    def get(self, request, *args, **kwargs):
        self.knowledge = get_object_or_404(Znanie, id=kwargs['pk'])
        if self.knowledge.tz.can_be_rated:
            return super().get(request, *args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        """
        Получение context
        """
        context = super().get_context_data(**kwargs)

        self.knowledge_id = self.kwargs.get('pk')
        copy_request = copy.copy(self.request)

        knowledge = Znanie.objects.get(id=self.knowledge_id)
        context['knowledge'] = knowledge

        users = get_group_users(self.request, self.knowledge_id)
        _, context['all_users'] = get_average_proof_base_and_common_grades(
            users, copy_request, knowledge)
        context['count_users'] = len(users)

        copy_request.GET = {"gender": "M"}
        male_users = get_group_users(copy_request, self.knowledge_id)
        _, context['male_users'] = get_average_proof_base_and_common_grades(
            male_users, copy_request, knowledge)
        context['count_male_users'] = len(male_users)

        copy_request.GET = {"gender": "F"}
        female_users = get_group_users(copy_request, self.knowledge_id)
        _, context['female_users'] = get_average_proof_base_and_common_grades(
            female_users, copy_request, knowledge)
        context['count_female_users'] = len(female_users)

        all_age_users_scale = AgeUsersScale.objects.all()
        context["age_scales_grades"] = []
        for age_users_scale in all_age_users_scale:
            copy_request.GET = {
                "gender": "",
                "min_age": str(age_users_scale.min_age),
                "max_age": str(age_users_scale.max_age),
            }
            age_users = get_group_users(copy_request, self.knowledge_id)
            _, grade = get_average_proof_base_and_common_grades(
                age_users, copy_request, knowledge)
            context["age_scales_grades"].append({
                "interval": str(age_users_scale),
                "min_age": age_users_scale.min_age,
                "max_age": age_users_scale.max_age,
                "count_users": len(age_users),
                "name": grade.name,
                "value": grade.value
            })

        return context
