from django.shortcuts import render, get_object_or_404
from homework.models import Product

def product_list(request):
    product = Product.objects.all()
    context = {"product" : product}
    return render(request, 'prod.html', context)

def product_detail(request, pk):
    product_1 = get_object_or_404(Product, pk=pk)
    context = {"product_1":product_1}
    return render(request, "product_detail.html", context)
