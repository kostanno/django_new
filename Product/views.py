from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from Product.forms import ProductForm
from Product.models import Product

class ProductListView(ListView):
    """Список всех товаров (доступно всем)"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 10


@login_required
def product_create_view(request):
    """Создание нового товара (только для авторизованных)"""
    if request.method == 'POST':
        # Логика создания товара
        pass
    return render(request, 'products/product_form.html')


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о товаре (только для авторизованных)"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


@login_required
def product_update_view(request, pk):
    """Редактирование товара (только для авторизованных)"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        # Логика обновления товара
        pass

    return render(request, 'products/product_form.html', {'product': product})


@login_required
def product_delete_view(request, pk):
    """Удаление товара (только для авторизованных)"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар успешно удален!')
        return redirect('product_list')

    return render(request, 'products/product_confirm_delete.html', {'product': product})


# Альтернативный вариант с классами и миксинами
class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание товара через класс (только для авторизованных)"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Товар успешно создан!')
        return super().form_valid(form)