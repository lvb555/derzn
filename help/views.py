import re

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render

from .models import HelpPage


def help(request):
    """
    1. The function receives data from which URL the transition to the Help page was made.
    2. Using a regular expression, we get the URL prefix:
       /drevo/ == /
       /drevo/labels/ == /labels
    3. We are looking for the help page for the desired menu item in the tag database.
    !!! For menu items for which there is no help page, help is called by the tag / !!!
    """
    url_path = re.search(r"(?<=drevo)/\w+|/$",
                         request.META.get('HTTP_REFERER')).group(0)
    try:
        context = HelpPage.objects.get(url_tag=url_path)
    except ObjectDoesNotExist:
        context = get_object_or_404(HelpPage, url_tag='/')
    return render(request, "help/help.html", {"context": context})
