from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Категории"""

    name = models.CharField(max_length=100, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар"""

    class PublicationStatus(models.TextChoices):
        DRAFT = 'draft', _('Черновик')
        UNDER_REVIEW = 'under_review', _('На проверке')
        PUBLISHED = 'published', _('Опубликован')
        UNPUBLISHED = 'unpublished', _('Снят с публикации')

    name = models.CharField(max_length=200, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    image = models.ImageField(
        upload_to="products/",
        verbose_name="Изображение",
        help_text="Загрузите изображение товара",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        blank=True,
        null=True,
        related_name="products",
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Цена за покупку"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата последнего изменения"
    )

    publication_status = models.CharField(
        _('Статус публикации'),
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='Владелец',
        related_name='products',
        null=True,
        blank=True
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='Владелец',
        related_name='products',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]
        permissions = [
            ('can_unpublish_product', 'Может снимать с публикации продукт'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and not self.publication_status:
            self.publication_status = self.PublicationStatus.UNDER_REVIEW
        super().save(*args, **kwargs)

    def is_owner(self, user):
        return self.owner == user


    def can_delete(self, user):
        if self.is_owner(user):
            return True
        if user.has_perm('products.delete_product'):
            return True
        return False


class ProductModerationLog(models.Model):

    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Модератор'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )
    action = models.CharField(_('действие'), max_length=50)
    details = models.TextField(_('детали'), blank=True)
    created_at = models.DateTimeField(_('дата действия'), auto_now_add=True)

    class Meta:
        verbose_name = 'Лог модерации продукта'
        verbose_name_plural = 'Логи модерации продуктов'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.moderator} - {self.action} - {self.created_at}"