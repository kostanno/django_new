from homework.views import product_list, product_detail
from homework.apps import HomeworkConfig
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

app_name = HomeworkConfig.name

urlpatterns = [
    path('', product_list, name= 'product_list'),
    path('homework/<int:pk>/',product_detail, name= 'product_detail')
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)