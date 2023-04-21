from django.core.exceptions import EmptyResultSet
from django.db.models import QuerySet
from django.template import Library, RequestContext
from django.utils.safestring import mark_safe
from drevo.utils.knowledge_tree_builder import KnowledgeTreeBuilder
from drevo.models import Znanie, Category, Tr, Author, UserParameters, SettingsOptions
from drevo.forms import AdvanceTreeSearchFrom

register = Library()


@register.inclusion_tag('drevo/tags/knowledge_tree.html', takes_context=True)
def build_knowledge_tree(context: RequestContext,
                         queryset: QuerySet[Znanie],
                         tree_num: int = 1,
                         show_searchbar: bool = True,
                         empty_tree_message: str = '',
                         show_only: Tr = None,
                         hidden_author: Author = None,
                         show_complex: bool = False,
                         edit_widgets: list[str] = None
                         ):
    """
        Тег для построения дерева знаний \n
        tree_num: номер дерева (на случай если необходимо на одной странице создать несколько деревьев); \n

        show_searchbar: отображать поле поиска по дереву; \n

        empty_tree_message: если дерево по какой либо причине нельзя построить, то будет выводиться сообщение указанное
        в данном параметре; \n

        show_only: принимает объект вида связи, если передан данный параметр, то будут отображаться только связи
        данного вида для переданных знаний (используется если у одного знания из queryset есть несколько связей разных
        видов и необходимо отобразить связи только определённого вида); \n

        hidden_author: принимает объект автора, около знаний данного автора он не указывается; \n

        show_complex: если данный параметр имеет значение True, то на дереве будут отображаться сложные знания.
        В настоящее время для отображения на дереве существует 2 вида сложных знаний: "Таблица", "Тест"

        edit_widgets: список виджетов для редактирования дерева. Допустимые значения: \n
        create - создать новую ветвь (связь)
        delete - удалить ветвь (связь)
        update - удалить ветвь (связь)
    """
    if not queryset:
        raise EmptyResultSet('Для построения дерева необходим queryset знаний')
    edit_mode = True if edit_widgets else False
    builder_kwargs = {
        'queryset': queryset, 'show_only': show_only, 'show_complex': show_complex, 'edit_mode': edit_mode
    }
    tree_builder = KnowledgeTreeBuilder(**builder_kwargs)
    tree_builder_context = tree_builder.get_nodes_data_for_tree()
    tree_context = dict(
        tree_num=tree_num,
        show_searchbar=show_searchbar,
        empty_tree_message=empty_tree_message,
        hidden_author=hidden_author,
        active_knowledge=queryset,
        **tree_builder_context
    )
    # Search block
    search_word = context.request.POST.get('search_word', '')

    param_names = (
        'Искать в поле "Содержание"', 'Искать в поле "Комментарий к источнику"', 'Учитывать структурные знания'
    )
    fields_by_param = {
        'Искать в поле "Содержание"': 'content',
        'Искать в поле "Комментарий к источнику"': 'source_com',
        'Учитывать структурные знания': 'use_struct'
    }

    if context.request.user.is_anonymous:
        params = SettingsOptions.objects.filter(name__in=param_names)
        user_search_param = {(fields_by_param.get(param.name), param.name): param.default_param for param in params}
        show_struct_param = True if user_search_param.get(('use_struct', 'Учитывать структурные знания')) else False
    else:
        user_params_queryset = (
            UserParameters.objects
            .select_related('param')
            .filter(user=context.request.user, param__name__in=param_names)
            .values('param__name', 'param_value')
        )
        user_search_param = {param.get('param__name'): param.get('param_value') for param in user_params_queryset}
        show_struct_param = True if user_search_param.get('Учитывать структурные знания') else False
        user_search_param = {(fields_by_param.get(name), name): value for name, value in user_search_param.items()}

    tree_context['user_search_param'] = user_search_param
    tree_knowledge = tree_builder.get_tree_knowledge_list(with_struct_knowledge=show_struct_param)
    tree_context['empty_result'] = context.request.GET.get('empty_result', '')
    tree_context['tree_knowledge'] = ','.join(list(map(str, tree_knowledge)))
    tree_context['search_word'] = search_word
    tree_context['is_advance_search'] = True if 'advance_search' in context.request.POST else False
    tree_context['edit_widgets'] = ''.join(edit_widgets).split(' ') if edit_widgets else []
    tree_context['user'] = context.request.user
    if tree_context['is_advance_search']:
        tree_context['form'] = AdvanceTreeSearchFrom(data=context.request.POST)
    return tree_context


@register.simple_tag
def get_data_by_category(tree_data: dict, category) -> list:
    return tree_data.get(category.pk)


@register.simple_tag
def get_relation_name(relations_names: dict, parent: Znanie, child: Znanie) -> str:
    if not parent:
        return ''
    return relations_names.get((parent.pk, child.pk))


@register.simple_tag
def get_relation_status(relations_status: dict, parent: Znanie, child: Znanie) -> str:
    if not parent:
        return ''
    return relations_status.get((parent.pk, child.pk))


@register.simple_tag
def get_require_widgets(widgets: list, status: str = None) -> list:
    if widgets == ['create', 'delete']:
        return widgets
    require_by_status = {
        'delete': ('WORK_PRE', 'WORK'),
        'update': ('WORK_PRE', 'WORK', 'PRE_READY', 'PRE_EXP', 'PRE_FIN', 'PRE_REJ', 'FIN', 'REJ')
    }
    return [widget for widget in widgets if status in require_by_status.get(widget)]


@register.simple_tag
def get_knowledge_counts(data, knowledge):
    counts = data.get(knowledge)
    if not counts:
        return ''
    knowledge_count = counts.get('knowledge_count')
    child_count = counts.get('child_count')

    if knowledge_count == child_count:
        html = f'<p class="badge kn_count">' \
               f'{knowledge_count}' \
               f'<span class="tooltip-text">Общее число знаний</span>' \
               f'</p>'
    elif child_count == 0:
        html = f'<p class="badge kn_count">' \
               f'{knowledge_count} ( )' \
               f'<span class="tooltip-text">Общее число знаний (Число дочерних знаний)</span>' \
               f'</p>'
    else:
        html = f'<p class="badge kn_count">' \
               f'{knowledge_count} ({child_count})' \
               f'<span class="tooltip-text">Общее число знаний (Число дочерних знаний)</span>' \
               f'</p>'
    return mark_safe(html)


@register.simple_tag
def get_category_counts(data, category):
    counts = data.get(category)
    if not counts:
        return ''
    knowledge_count = counts.get('knowledge_count')
    base_knowledge_count = counts.get('base_knowledge_count')

    if knowledge_count == base_knowledge_count:
        html = f'<p class="badge kn_count">' \
               f'{knowledge_count}' \
               f'<span class="tooltip-text">Общее число знаний</span>' \
               f'</p>'
    elif base_knowledge_count == 0:
        html = f'<p class="badge kn_count">' \
               f'{knowledge_count} ( )' \
               f'<span class="tooltip-text">Общее число знаний (Число основных знаний)</span>' \
               f'</p>'
    else:
        html = f'<p class="badge kn_count">' \
               f'{knowledge_count} ({base_knowledge_count})' \
               f'<span class="tooltip-text">Общее число знаний (Число основных знаний)</span>' \
               f'</p>'
    return mark_safe(html)
