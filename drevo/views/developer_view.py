from django.shortcuts import render
from drevo.models.developer import Developer

def developer_view(request):
    """
    Отображаем страницу Разработчики
    """
    filter = request.GET.get("filter")
    developers_list = Developer.objects.order_by('-contribution')
    filter_ = False

    if filter == 'name':
        filter_ = True
        developers = []
        for developer in developers_list:
            developers.append(developer)
        def swap(i, j):
            developers[i], developers[j] = developers[j], developers[i]

        n = len(developers)
        swapped = True

        x = -1
        while swapped:
            swapped = False
            x = x + 1
            for i in range(1, n-x):
                if developers[i - 1].name[0] > developers[i].name[0]:
                    swap(i - 1, i)
                    swapped = True
        developers_list = developers

    context = {
        'developers_list': developers_list,
        'filter': filter_,
        }
    return render(request, 'drevo//developer_page.html', context)   