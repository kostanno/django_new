from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from .models import Product, Category, ProductModerationLog
from .forms import ProductForm, ProductFilterForm


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание нового товара - ТОЛЬКО для авторизованных пользователей"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def get_form_kwargs(self):
        """Передаем request в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Автоматическое присваивание владельца (ЗАДАНИЕ 2)"""
        # ОБЯЗАТЕЛЬНО устанавливаем владельца = текущий пользователь
        form.instance.owner = self.request.user

        # Если пользователь - модератор или суперпользователь, можно сразу опубликовать
        if self.request.user.has_perm('products.can_edit_any_product') or self.request.user.is_superuser:
            form.instance.publication_status = Product.PublicationStatus.PUBLISHED
        else:
            # Обычные пользователи отправляют на проверку
            form.instance.publication_status = Product.PublicationStatus.UNDER_REVIEW

        response = super().form_valid(form)

        # Сообщения в зависимости от статуса
        if form.instance.publication_status == Product.PublicationStatus.PUBLISHED:
            messages.success(self.request, _('Продукт успешно создан и опубликован!'))
        elif form.instance.publication_status == Product.PublicationStatus.UNDER_REVIEW:
            messages.success(self.request, _('Продукт успешно создан и отправлен на проверку!'))

        return response

    def get_context_data(self, **kwargs):
        """Добавляем информацию о текущем пользователе в контекст"""
        context = super().get_context_data(**kwargs)
        context['is_moderator'] = (
                self.request.user.has_perm('products.can_edit_any_product') or
                self.request.user.is_superuser
        )
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование товара - ТОЛЬКО для владельцев и модераторов"""
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def get_form_kwargs(self):
        """Передаем request в форму"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        """Проверяем права доступа перед отображением страницы (ЗАДАНИЕ 2)"""
        product = self.get_object()
        user = request.user

        # Разрешаем доступ если:
        # 1. Пользователь владелец продукта
        # 2. Пользователь модератор (имеет право can_edit_any_product)
        # 3. Пользователь суперпользователь
        # 4. Пользователь в группе "Модератор продуктов" И имеет право изменения продукта

        can_edit = (
                product.owner == user or  # Владелец
                user.has_perm('products.can_edit_any_product') or  # Модератор с правом редактирования
                user.is_superuser or  # Суперпользователь
                (user.groups.filter(name='Модератор продуктов').exists() and
                 user.has_perm('products.change_product'))  # Пользователь в группе модераторов
        )

        if not can_edit:
            messages.error(
                request,
                _('У вас нет прав для редактирования этого продукта! Только владелец или модератор могут редактировать продукт.')
            )
            return redirect('product_detail', pk=product.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Обновляем информацию о последнем редактировании"""
        messages.success(self.request, _('Продукт успешно обновлен!'))

        # Логируем действие, если редактирует модератор (не владелец)
        if not self.object.is_owner(self.request.user) and (
                self.request.user.has_perm('products.can_edit_any_product') or
                self.request.user.groups.filter(name='Модератор продуктов').exists()
        ):
            ProductModerationLog.objects.create(
                moderator=self.request.user,
                product=self.object,
                action='edit_by_moderator',
                details=f'Продукт отредактирован модератором {self.request.user.email}'
            )
            messages.info(self.request, _('Продукт отредактирован модератором.'))

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Добавляем информацию о правах в контекст"""
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        user = self.request.user

        context['is_owner'] = product.owner == user
        context['is_moderator'] = (
                user.has_perm('products.can_edit_any_product') or
                user.groups.filter(name='Модератор продуктов').exists() or
                user.is_superuser
        )

        return context


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление товара - ТОЛЬКО для владельцев и модераторов"""
    model = Product
    template_name = 'products/product_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('product_list')

    def dispatch(self, request, *args, **kwargs):
        """Проверяем права доступа перед отображением страницы (ЗАДАНИЕ 2)"""
        product = self.get_object()
        user = request.user

        # Разрешаем доступ если:
        # 1. Пользователь владелец продукта
        # 2. Пользователь имеет право delete_product (модератор)
        # 3. Пользователь суперпользователь
        # 4. Пользователь в группе "Модератор продуктов"
        # 5. Пользователь имеет кастомное право can_delete_any_product

        can_delete = (
                product.owner == user or  # Владелец
                user.has_perm('products.delete_product') or  # Модератор с правом удаления
                user.has_perm('products.can_delete_any_product') or  # Кастомное право удаления
                user.is_superuser or  # Суперпользователь
                user.groups.filter(name='Модератор продуктов').exists()  # В группе модераторов
        )

        if not can_delete:
            messages.error(
                request,
                _('У вас нет прав для удаления этого продукта! Только владелец или модератор могут удалить продукт.')
            )
            return redirect('product_detail', pk=product.pk)

        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Переопределяем удаление для логирования и сообщений"""
        product = self.get_object()
        user = request.user

        # Логируем действие, если удаляет модератор (не владелец)
        if not product.is_owner(user) and (
                user.has_perm('products.delete_product') or
                user.groups.filter(name='Модератор продуктов').exists()
        ):
            ProductModerationLog.objects.create(
                moderator=user,
                product=product,
                action='delete_by_moderator',
                details=f'Продукт удален модератором {user.email}. Владелец: {product.owner.email if product.owner else "Не указан"}'
            )
            messages.info(request, _('Продукт удален модератором.'))
        else:
            messages.success(request, _('Продукт успешно удален!'))

        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Добавляем информацию о правах в контекст"""
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        user = self.request.user

        context['is_owner'] = product.owner == user
        context['is_moderator'] = (
                user.has_perm('products.delete_product') or
                user.groups.filter(name='Модератор продуктов').exists() or
                user.is_superuser
        )

        return context


@login_required
def unpublish_product(request, pk):
    """Снятие продукта с публикации - ТОЛЬКО для модераторов"""
    product = get_object_or_404(Product, pk=pk)

    # ПРОВЕРКА ПРАВ (ЗАДАНИЕ 1) - ТОЛЬКО модераторы
    can_unpublish = (
            request.user.has_perm('products.can_unpublish_product') or
            request.user.has_perm('products.can_edit_any_product') or
            request.user.is_superuser or
            request.user.groups.filter(name='Модератор продуктов').exists()
    )

    if not can_unpublish:
        messages.error(
            request,
            _('У вас нет прав для снятия продукта с публикации! Только модераторы могут выполнять это действие.')
        )
        return redirect('product_detail', pk=product.pk)

    # Проверяем, что продукт опубликован
    if product.publication_status != Product.PublicationStatus.PUBLISHED:
        messages.warning(request, _('Продукт не опубликован!'))
        return redirect('product_detail', pk=product.pk)

    # Снимаем с публикации
    product.publication_status = Product.PublicationStatus.UNPUBLISHED
    product.save()

    # Логируем действие
    ProductModerationLog.objects.create(
        moderator=request.user,
        product=product,
        action='unpublish',
        details=_('Продукт снят с публикации модератором')
    )

    messages.success(request, _('Продукт успешно снят с публикации!'))
    return redirect('product_detail', pk=product.pk)


@login_required
def publish_product(request, pk):
    """Публикация продукта - ТОЛЬКО для владельцев"""
    product = get_object_or_404(Product, pk=pk)

    # Проверяем, является ли пользователь владельцем
    if product.owner != request.user:
        messages.error(
            request,
            _('Вы можете публиковать только свои продукты! Только владелец может отправить продукт на публикацию.')
        )
        return redirect('product_detail', pk=product.pk)

    # Проверяем текущий статус
    if product.publication_status == Product.PublicationStatus.PUBLISHED:
        messages.warning(request, _('Продукт уже опубликован!'))
    else:
        # Устанавливаем статус "На проверке"
        product.publication_status = Product.PublicationStatus.UNDER_REVIEW
        product.save()

        messages.success(request, _('Продукт отправлен на проверку для публикации!'))

    return redirect('product_detail', pk=product.pk)


@login_required
def approve_product(request, pk):
    """Одобрение продукта для публикации - ТОЛЬКО для модераторов"""
    product = get_object_or_404(Product, pk=pk)

    # Проверка прав модератора
    is_moderator = (
            request.user.has_perm('products.can_edit_any_product') or
            request.user.is_superuser or
            request.user.groups.filter(name='Модератор продуктов').exists()
    )

    if not is_moderator:
        messages.error(
            request,
            _('У вас нет прав для одобрения продуктов! Только модераторы могут одобрять публикацию.')
        )
        return redirect('product_detail', pk=product.pk)

    # Одобряем продукт
    product.publication_status = Product.PublicationStatus.PUBLISHED
    product.save()

    # Логируем действие
    ProductModerationLog.objects.create(
        moderator=request.user,
        product=product,
        action='approve',
        details=_('Продукт одобрен для публикации модератором')
    )

    messages.success(request, _('Продукт одобрен и опубликован!'))
    return redirect('product_detail', pk=product.pk)
