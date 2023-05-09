import codecs
import csv

from django.core.management import BaseCommand

from ...models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        csvfile = codecs.open('ingredients.csv', 'r', encoding='utf-8')
        reader = csv.reader(csvfile)
        for row in reader:
            name, measurement_unit = row
            ingredient = Ingredient.objects.create(
                name=name.strip(),
                measurement_unit=measurement_unit.strip()
            )
