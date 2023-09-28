import json

from django.core.management.base import BaseCommand
from foodgram.settings import BASE_DIR
from tqdm import tqdm

from recipes.models import Ingredient


class Command(BaseCommand):

    help = 'Импорт csv файлов в таблицы базы'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE(
            'Начинаем процесс переноса данных из json в Базу данных '))

        with open(
            f'{BASE_DIR}/data/ingredients.json', encoding='utf-8', mode='r'
        ) as file:
            json_read = json.load(file)
            pbar = tqdm(json_read)

            for ingredient in json_read:
                pbar.set_description('Processing %s ' % ingredient['name'])
                pbar.update()

                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )

            self.stdout.write(self.style.SUCCESS(
                '\n Данные успешно перенесены'))
