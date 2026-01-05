from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from product.models import Product


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(Product)
        self.create_product_moderator_group(content_type)
        self.create_product_owner_group(content_type)
        self.stdout.write(self.style.SUCCESS('Все группы успешно созданы!'))

    def create_product_moderator_group(self, content_type):
        """Создает группу модераторов продуктов"""
        group_name = 'Модератор продуктов'
        permissions = [
            Permission.objects.get(
                codename='can_unpublish_product',
                content_type=content_type
            ),
            Permission.objects.get(
                codename='delete_product',
                content_type=content_type
            ),
            Permission.objects.get(
                codename='change_product',
                content_type=content_type
            ),
            Permission.objects.get(
                codename='view_product',
                content_type=content_type
            ),
        ]

        group, created = Group.objects.get_or_create(name=group_name)
        for perm in permissions:
            group.permissions.add(perm)
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Группа "{group_name}" создана и права назначены'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'Группа "{group_name}" уже существовала, права обновлены'
            ))

        return group

    def create_product_owner_group(self, content_type):
        """Создает группу владельцев продуктов"""
        group_name = 'Владелец продуктов'
        permissions = [
            Permission.objects.get(
                codename='add_product',
                content_type=content_type
            ),
            Permission.objects.get(
                codename='change_product',
                content_type=content_type
            ),
            Permission.objects.get(
                codename='delete_product',
                content_type=content_type
            ),
            Permission.objects.get(
                codename='view_product',
                content_type=content_type
            ),
        ]

        group, created = Group.objects.get_or_create(name=group_name)
        for perm in permissions:
            group.permissions.add(perm)
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Группа "{group_name}" создана и права назначены'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'Группа "{group_name}" уже существовала, права обновлены'
            ))

        return group