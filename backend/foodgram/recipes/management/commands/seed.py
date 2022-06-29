import json

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Seeds the database with ingredients'

    def handle(self, *args, **options):
        path = settings.BASE_DIR / '..' / '..' / 'data' / 'ingredients.json'
        with open(path) as f:
            ingredients = json.loads(f.read())
            for ingredient in ingredients:
                Ingredient.objects.create(**ingredient)
            msg = 'Successfully seeded the database with ingredients'
            self.stdout.write(self.style.SUCCESS(msg))
