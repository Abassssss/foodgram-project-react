import json

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Seeds the database with ingredients"

    def handle(self, *args, **options):
        path = settings.BASE_DIR / ".." / ".." / "data" / "ingredients.json"
        with open(path, encoding="utf-8") as f:
            ingredients = json.loads(f.read())
            Ingredient.objects.bulk_create(
                Ingredient(**ing) for ing in ingredients
            )
            msg = "Successfully seeded the database with ingredients"
            self.stdout.write(self.style.SUCCESS(msg))
