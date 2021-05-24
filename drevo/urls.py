from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import DrevoListView, DrevoView, ZnanieDetailView, ZnanieByLabelView

urlpatterns = [
    path('category/<int:pk>', DrevoListView.as_view(), name = 'drevo_type'),
    path('drevo/', DrevoView.as_view(), name = 'drevo'),
    path('znanie/<int:pk>', ZnanieDetailView.as_view(), name = 'zdetail'),
    path('label/<int:pk>', ZnanieByLabelView.as_view(), name = 'zlabel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)