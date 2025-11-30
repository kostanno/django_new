from django.urls import path
from homework.views import product_list, product_detail
from homework.apps import HomeworkConfig


app_name = HomeworkConfig.name

urlpatterns = [
    path('', product_list),
    path('homework/<int:pk>/',product_detail,name= 'product_detail')
    ]