from django.core.cache import cache
from django.db.models import Prefetch

from .models import Product, Category


def get_products_by_category(category_slug):
    try:
        category = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(
            category=category,
            is_available=True
        ).select_related('category')
        return products
    except Category.DoesNotExist:
        return Product.objects.none()


def get_category_tree():
    cache_key = 'category_tree'
    categories = cache.get(cache_key)
    if categories is None:
        categories = Category.objects.filter(
            parent__isnull=True
        ).prefetch_related('children')
        cache.set(cache_key, categories, 60 * 60)

    return categories


def get_cached_products_by_category(category_slug, force_refresh=False):
    """
    Получение продуктов по категории с низкоуровневым кешированием
    """
    cache_key = f'products_category_{category_slug}'
    if force_refresh:
        cache.delete(cache_key)
    products = cache.get(cache_key)
    if products is None:
        products = Product.objects.filter(
            category__slug=category_slug,
            is_available=True
        ).select_related(
            'category'
        ).prefetch_related(
            Prefetch('images')
        ).order_by('-created_at')
        cache.set(cache_key, products, 60 * 30)

        print(f"Кешировано {len(products)} продуктов для категории {category_slug}")

    return products