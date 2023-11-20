from django import template
from django.db.models import QuerySet
from django.template import RequestContext

from drevo.models import Znanie, QuestionToKnowledge, UserAnswerToQuestion, Relation
from .knowledge_tree import build_knowledge_tree

register = template.Library()


@register.filter()
@register.inclusion_tag('drevo/tags/constructors_tree.html', takes_context=True)
def build_constructor_tree(context: RequestContext,
                           queryset: QuerySet[Znanie],
                           show_complex: bool = True,
                           is_constructor_type: str = None
                           ):
    return build_knowledge_tree(context=context, show_searchbar=False, queryset=queryset, show_complex=show_complex,
                                is_constructor_type=is_constructor_type)


@register.simple_tag
def is_questions_and_answers_for_algorithm(knowledge: Znanie) -> bool:
    """Проверка, есть ли привязанные к знанию в алгоритме вопрос(ы) пользователям и ответ(ы)"""
    return (QuestionToKnowledge.objects.filter(knowledge=knowledge).exists()
            and UserAnswerToQuestion.objects.filter(knowledge=knowledge).exists())


@register.simple_tag
def is_max_number_of_inner_rels_for_zn(knowledge: Znanie) -> bool:
    """Возвращает True, если создано максимально возможное количество внутренних связей для знания.
    Примечание: в ходе проверки никогда не учитываются связи вида «Далее»."""
    existing_relations_count = Relation.objects.filter(bz=knowledge).distinct().exclude(tr__name='Далее').count()
    return knowledge.tz.max_number_of_inner_rels == existing_relations_count
