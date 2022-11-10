from django.shortcuts import render
from drevo.models.developer import Developer

def developer_view(request):
    """
    Отображаем страницу Разработчики
    """
    developers_list = Developer.objects.order_by('-contribution')
    context = {'developers_list': developers_list}
    return render(request, 'drevo//developer_page.html', context)   