from django.views import View
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Product
from .services import get_products_by_category, get_category_tree
from .utils import is_cache_enabled


class ProductDetailView(View):
    @method_decorator(cache_page(60 * 15, key_prefix='product_detail'))
    def get(self, request, product_id):
        product = get_object_or_404(
            Product.objects.select_related('category'),
            id=product_id
        )

        related_products = get_related_products(product)
        context = {
            'product': product,
            'related_products': related_products,
        }

        return render(request, 'products/product_detail.html', context)

class CategoryProductsView(View):
    """
    Представление для отображения продуктов по категории
    """

    def get(self, request, category_slug):
        products = get_products_by_category(category_slug)
        categories = get_category_tree()

        context = {
            'products': products,
            'categories': categories,
            'current_category_slug': category_slug,
            'cache_enabled': is_cache_enabled(),
        }

        return render(request, 'products/category_products.html', context)


class CacheControlView(View):
    """
    Представление для управления кешированием (опционально)
    """

    def get(self, request):
        context = {
            'cache_enabled': is_cache_enabled(),
            'cache_timeout': getattr(settings, 'CACHE_TTL', 900),
        }
        return render(request, 'products/cache_control.html', context)

    def post(self, request):
        action = request.POST.get('action')

        if action == 'clear_cache':
            from django.core.cache import cache
            cache.clear()
            messages.success(request, 'Кеш успешно очищен')
        elif action == 'toggle_cache':
            current = is_cache_enabled()
            settings.CACHE_ENABLED = not current
            status = 'включено' if not current else 'выключено'
            messages.success(request, f'Кеширование {status}')

        return redirect('cache_control')