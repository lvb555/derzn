from django.shortcuts import Http404, get_object_or_404
from django.views.generic import TemplateView
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_grade_scale import KnowledgeGradeScale
from drevo.models.knowledge_grade import KnowledgeGrade
from drevo.models.relation import Relation

class InfographicsView(TemplateView):
    template_name = 'drevo/infographics.html'

    def get(self, request, *args, **kwargs):
        self.knowledge = get_object_or_404(Znanie, id=kwargs['pk'])
        if self.knowledge.tz.can_be_rated:
            return super().get(request, *args, **kwargs)
        raise Http404

    def get_context_data(self, **kwargs):
        '''
        Функция для получения контекста
        '''
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            knowledge = Znanie.objects.prefetch_related('base').get(
                id=self.kwargs.get('pk'))
            context["base_grade"] = KnowledgeGrade.objects.filter(
                knowledge=knowledge,
                user=self.request.user,
            ).first()
            context['knowledge'] = knowledge
            context['grade_scales'] = KnowledgeGradeScale.objects.all()

            proof_relations = knowledge.base.filter(
                tr__is_argument=True,
                rz__tz__can_be_rated=True,
            )

            context['proof_relations'] = proof_relations

            common_grade_value, proof_base_value = knowledge.get_common_grades(
                request=self.request)

            if proof_base_value is not None:
                context['proof_base_value'] = proof_base_value
                context['proof_base_grade'] = \
                    KnowledgeGradeScale.get_grade_object(proof_base_value)
            if common_grade_value is not None:
                context['common_grade_value'] = common_grade_value
                context['common_grade'] = KnowledgeGradeScale.get_grade_object(
                    common_grade_value)

            self.index_element_tree = 0
            context['elements_tree'] = self.get_elements_tree(proof_relations)
        return context

    def get_colors_from_knowledge(self, relation: Relation, lvl_against: int,
                            father_relation: Relation|None) -> tuple[str, str]:
        '''
        Получение цвета знания

        - relation - связь от родительского знания к знанию, для которого
                     определяется цвет
        - lvl_against - уровень довода против, т.е. если, к примеру, родитель
                        довод против и знание, для которого определяем цвет,
                        то будет уровень равнятся 2
        - father_relation - родительская связь
        '''
        bg_color = "#FFFFFF"
        font_color = "#000000"
        try:
            grade = KnowledgeGrade.objects.get(
                knowledge=relation.rz,
                user=self.request.user,
            )
            father_argument_type = False
            if father_relation is not None:
                father_argument_type = father_relation.tr.argument_type

            if any((all((not father_argument_type,relation.tr.argument_type)),
                    all((father_argument_type, 
               any((all((not relation.tr.argument_type, lvl_against % 2 == 0)),
                    all((not relation.tr.argument_type, lvl_against % 2 != 0))
               )))))):
                bg_color = grade.grade.contraargument_color_background
                font_color = grade.grade.contraargument_color_font
            elif any((all((not father_argument_type,
                           not relation.tr.argument_type)),
                    all((father_argument_type, 
               any((all((relation.tr.argument_type, lvl_against % 2 == 0)),
                    all((relation.tr.argument_type, lvl_against % 2 != 0))
               )))))):
                bg_color = grade.grade.argument_color_background
                font_color = grade.grade.argument_color_font
        except KnowledgeGrade.DoesNotExist:
            pass
        return bg_color, font_color

    def get_elements_tree(self, relations: list[Relation], lvl_up: bool=False,
                          lvl_against: int=-1,
                          father_relation: Relation|None = None) -> list[dict]:
        '''
        Получение элементов дерева

        - relations - связи, с помощью которых должны получить элементы дерева
        - lvl_up - переменная для определения нужно ли по дереву подниматься
                   на уровень выше
        - lvl_against - уровень довода против, т.е. если, к примеру, родитель
                        довод против и знание, для которого определяем цвет,
                        то будет уровень равнятся 2
        - father_relation - родительская связь
        - возвращается лист из словарей, который имеет следующую структуру:
          [
            {
              "name": имя знания,
              "bg_color": цвет фона,
              "font_color": цвет шрифта,
              "for_or_against": буква обозначающая какой это довод - за или
                                против,
              "has_childrens": есть ли у этого знания сыновья,
              "id": идентификатор элемента дерева,

              необязательные параметры:
              "lvl_up": переменная для определения нужно ли по дереву
                        подниматься на уровень выше,
              "lvl_down": переменная для определения нужно ли по дереву
                          подниматься на уровень ниже
            },
            ...
          ]
        '''
        tree = []
        for relation in relations:
            if not relation.tr.argument_type:
                lvl_against = -1
            elif relation.tr.argument_type and (father_relation is None \
                                    or not father_relation.tr.argument_type):
                lvl_against = 1
            elif relation.tr.argument_type and \
                    father_relation.tr.argument_type:
                lvl_against += 1

            if relation.tr.is_argument:
                knowledge = relation.rz
                childrens_knowledge = Relation.objects.filter(bz=knowledge)
                bg_color, font_color = self.get_colors_from_knowledge(
                    relation, lvl_against, father_relation)
                tree.append({
                    "name": knowledge.name,
                    "bg_color": bg_color,
                    "font_color": font_color,
                    "lvl_up": lvl_up,
                    "for_or_against":"К" if relation.tr.argument_type else "А",
                    "has_childrens": bool(childrens_knowledge),
                    "id": self.index_element_tree,
                })
                self.index_element_tree += 1

                if lvl_up:
                    lvl_up = False

                if childrens_knowledge:
                    tree += self.get_elements_tree(childrens_knowledge,
                                                   True, lvl_against,
                                                   relation)
                    tree.append({"lvl_down": True})
        return tree
