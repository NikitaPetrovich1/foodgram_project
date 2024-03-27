import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        file_name = 'ingredients.csv'
        csv_path = f'{settings.BASE_DIR}/data/{file_name}'

        try:
            with open(csv_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                ingredients_data = [
                    {
                        'name': row['name'],
                        'measurement_unit': row['measurement_unit']
                    } for row in reader
                ]

            Ingredient.objects.bulk_create(
                [Ingredient(**ingredient) for ingredient in ingredients_data]
            )

            self.stdout.write(self.style.SUCCESS(
                f'Successfully created {len(ingredients_data)}'
                f' Ingredient objects from {csv_path}'
            ))

        except FileNotFoundError:
            print(f'Файл {file_name} не найден.')
