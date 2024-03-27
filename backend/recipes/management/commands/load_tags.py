import csv

from django.core.management.base import BaseCommand
from recipes.models import Tag
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        file_name = 'tags.csv'
        csv_path = f'{settings.BASE_DIR}/data/{file_name}'

        try:
            with open(csv_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                tags_data = [
                    {
                        'name': row['name'],
                        'color': row['color'],
                        'slug': row['slug']
                    } for row in reader
                ]

            Tag.objects.bulk_create(
                [Tag(**tag) for tag in tags_data]
            )

            self.stdout.write(self.style.SUCCESS(
                f'Successfully created {len(tags_data)}'
                f' Tags objects from {csv_path}'
            ))

        except FileNotFoundError:
            print(f'Файл {file_name} не найден.')
