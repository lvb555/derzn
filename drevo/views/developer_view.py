from django.shortcuts import render
from drevo.models.developer import Developer

def developer_view(request):
    """
    Отображаем страницу Разработчики
    """
    filter = request.GET.get("filter")
    filter_ = False
    if filter == 'name':
        filter_ = True
        developers_list = Developer.objects.order_by('name')
    else:
        developers_list = Developer.objects.order_by('-contribution')

    context = {
        'developers_list': developers_list,
        'filter': filter_,
        }
    return render(request, 'drevo//developer_page.html', context)   