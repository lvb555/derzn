import re
from django.shortcuts import get_object_or_404, render

from .models import HelpPage


def help(request):
    """
    1. Функция получает данные из какого URL был осуществлен переход на страницу помощи.
    2. Используя регулярное выражение, получаем префикс URL:
       /drevo/ == /
       /drevo/labels/ == /labels
    3. Из БД вызывается объект HelpPage(Помощи) для нужного пункта меню.
    !!! Пункты меню, для которых нет страницы помощи
        или переход происходит со строннего ресурса по ссылке
        по умолчанию вызываются с тегом '/' !!!
    !!! Если в БД, нет объектов HelpPage, вызывается 404!!!
    """
    try:
        url_path = re.search(r"(?<=drevo)/\w+|/$",
                             request.META.get('HTTP_REFERER')).group(0)
        context = HelpPage.objects.get(url_tag=url_path)
    except Exception:
        context = get_object_or_404(HelpPage, url_tag='/')

    return render(request, "help/help.html", {"context": context})
