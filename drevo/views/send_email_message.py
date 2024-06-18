from django.shortcuts import get_object_or_404
from drevo.relations_tree import get_knowledges_by_categories
from drevo.sender import send_email
from drevo.models import Znanie, Relation, Category
from collections import Counter
from django.template.loader import render_to_string
from loguru import logger
from dz import settings

logger.add(
    "logs/main.log", format="{time} {level} {message}", rotation="100Kb", level="INFO"
)


def send_email_messages():
    all_new_knowledges = Znanie.objects.filter(is_published=True, date__gte='2023-02-26', tz__is_systemic=False,
                                               notification=False).exclude(author=None)
    # Берем все знания, включая дополнительные
    categories, knowledges = get_knowledges_by_categories(all_new_knowledges)
    set_with_users_info = set()
    for category_name, knowledge_list in knowledges.items():
        all_knowledges = knowledge_list['base'] + knowledge_list['additional']
        # Проверяем, есть ли категория
        if category_name != 'None':
            category = Category.objects.get(name=category_name)
            knowledge_categories = category.get_ancestors(include_self=True)
            for knowledge_category in knowledge_categories:
                user_to_notify = set(knowledge_category.subscribers.all())
            for obj in all_knowledges:
                user_to_notify = user_to_notify | set(obj.author.subscribers.all())
                for knowledge_tags in obj.labels.all():
                    # Объеденяем множества. Так не будут повторяться пользовотели, которым нужно отправить уведомление.
                    user_to_notify = user_to_notify | set(knowledge_tags.subscribers.all())
                # Меняем значение поля "Уведомление"
                obj.notification = True
                obj.save(update_fields=["notification"])
                set_with_users_info = set_with_users_info | user_to_notify

    if not set_with_users_info:
        return 0

    for user_to_send in set_with_users_info:
        knowledge_by_author = []
        knowledge_by_tags = []
        knowledge_by_categories = []
        new_knowledge = set()
        for category_name, knowledge_list in knowledges.items():
            if category_name != 'None':
                all_knowledges = knowledge_list['base'] + knowledge_list['additional']
                category_by_name = Category.objects.get(name=category_name)
                for obj in all_knowledges:
                    if user_to_send in set(obj.author.subscribers.all()):
                        knowledge_by_author.append(obj.author.name)
                        new_knowledge.add(obj)
                    for knowledge_tags in obj.labels.all():
                        if user_to_send in set(knowledge_tags.subscribers.all()):
                            knowledge_by_tags.append(knowledge_tags.name)
                            new_knowledge.add(obj)
                    if user_to_send in set(category_by_name.subscribers.all()):
                            knowledge_by_categories.append(category_by_name.name)
                            new_knowledge.add(obj)
        # Очищаем поле со знаниями, которые были при прошлой рассылки и добавляем новые
        user_to_send.knowledge_to_notification_page.clear()
        for knowledge in new_knowledge:
            obj = get_object_or_404(Znanie, pk=knowledge.pk)
            user_to_send.knowledge_to_notification_page.add(obj)
        author_sub = make_sentence(knowledge_by_author, 'от автора')
        tags_sub = make_sentence(knowledge_by_tags, 'по тегу')
        category_sub = make_sentence(knowledge_by_categories, 'в категории')

        message_subject = "Новое знание"

        context = {
            'page_url': settings.BASE_URL + '/drevo/new_knowledges/'+str(user_to_send.id)+'/',
            'author_sub': author_sub,
            'tags_sub': tags_sub,
            'category_sub': category_sub
        }

        patr = ""
        if user_to_send.first_name and user_to_send.patronymic:

            patr = ' ' + user_to_send.patronymic
        appeal = user_to_send.first_name or 'пользователь'

        context['appeal'] = appeal
        context['patr'] = patr

        message_text = render_to_string('email_templates/subscribe_notify_email.txt', context)
        message_html = render_to_string('email_templates/subscribe_notify_email.html', context)
        send_email(user_to_send.email, message_subject, message_html, message_text)
    return len(set_with_users_info)

def make_sentence(sub_info, sub):
    if sub_info:
        final_list = []
        if sub != 'от автора':
            for sub_obj in Counter(sub_info):
                final_list.append(f'"{sub_obj}" - {Counter(sub_info)[sub_obj]}')
            return final_list
        else:
            for sub_obj in Counter(sub_info):
                final_list.append(f'{sub_obj} - {Counter(sub_info)[sub_obj]}')
            return final_list
    else:
        return ''
