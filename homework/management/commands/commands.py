from django.core.management.base import BaseCommand
from homework.models import Category, Product


class Command(BaseCommand):

    help = "Add test students to the database"

    def handle(self, *args, **kwargs):

        Product.objects.all().delete()
        Category.objects.all().delete()
        group, _ = Product.objects.get_or_create(name="")

        test = [
            {"first_name": "Арбуз", "description": "Зеленый"},
            {"first_name": "Арбуз", "description": "Красный"},
            {"first_name": "Арбуз", "description": "Желтый"},
        ]

        for student_data in test:
            test, created = Product.objects.get_or_create(**student_data)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully added student: {test.first_name} {test.last_name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Student already exists: {test.first_name} {test.last_name}"
                    )
                )
