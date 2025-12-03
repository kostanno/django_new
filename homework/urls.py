from homework.views import ProductListView, ProductDetailView
from homework.apps import HomeworkConfig
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

app_name = HomeworkConfig.name

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)