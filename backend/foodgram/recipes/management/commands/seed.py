import json
import random
import shutil
from operator import itemgetter

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database"

    def handle(self, *args, **options):
        self._create_ingredients()
        tags = self._create_tags()
        users = self._create_users()
        self._create_recipes(users, tags)
        msg = "Successfully seeded the database"
        self.stdout.write(self.style.SUCCESS(msg))

    def _create_ingredients(self):
        path = settings.BASE_DIR / ".." / ".." / "data" / "ingredients.json"
        with open(path, encoding="utf-8") as f:
            ingredients = json.loads(f.read())
            Ingredient.objects.bulk_create(
                Ingredient(**i) for i in ingredients
            )

    def _create_tags(self):
        tags_data = [
            {"name": "Завтрак", "color": "#ADD8E6", "slug": "breakfast"},
            {"name": "Обед", "color": "#FFA500", "slug": "lunch"},
            {"name": "Ужин", "color": "#8B00FF", "slug": "dinner"},
        ]

        map_obj = map(
            itemgetter(0),
            [Tag.objects.get_or_create(**data) for data in tags_data],
        )
        return list(map_obj)

    def _create_users(self):
        users = []

        for i in range(3):
            user, created = User.objects.get_or_create(
                username=f"test{i}",
                email=f"test{i}@mail.ru",
                first_name=f"Test {i}",
                last_name=f"Test {i}",
            )

            if created:
                user.set_password(f"test{i}")
                user.save()

            users.append(user)

        return users

    def _create_recipes(self, users, tags):
        random.seed(420)
        # TODO: add ingredients.
        recipes_data = [
            {
                "name": "хлеб",
                "image": "lomtik-hleba.jpg",
                "text": "Берем хлеб и готово.",
                "cooking_time": 2,
            },
            {
                "name": "пирожки",
                "image": "pirojki.png",
                "text": "Берем пирожки и готово.",
                "cooking_time": 60,
            },
            {
                "name": "яйца",
                "image": "egg.png",
                "text": "Берем яйца и готово.",
                "cooking_time": 10,
            },
            {
                "name": "пельмени",
                "image": "pelmen.jfif",
                "text": "Берем пельмени и готово.",
                "cooking_time": 10,
            },
            {
                "name": "хлопья с молоком",
                "image": "hlopya.jpg",
                "text": "Берем хлопья с молоком и готово.",
                "cooking_time": 2,
            },
            {
                "name": "арбузель",
                "image": "arbuz.jpg",
                "text": "Берем арбуз и готово.",
                "cooking_time": 2,
            },
            {
                "name": "пицца",
                "image": "pizza.jpg",
                "text": "Берем пиццу и готово.",
                "cooking_time": 30,
            },
            {
                "name": "картошка фри",
                "image": "french-fries.jpg",
                "text": "Берем картошку фри и готово.",
                "cooking_time": 30,
            },
        ]

        for data in recipes_data:
            image = data.pop("image")
            data["author"] = random.choice(users)
            recipe, created = Recipe.objects.get_or_create(
                **data, image=f"recipes/{image}"
            )
            if created:
                shutil.copy(
                    settings.BASE_DIR / ".." / ".." / "data" / image,
                    settings.MEDIA_ROOT / "recipes" / image,
                )
                recipe.tags.set(
                    random.sample(tags, random.randrange(len(tags)))
                )
