import os

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from foodgram.settings import MIN_AMOUNT, MIN_COOK_TIME


class Tag(models.Model):
    name = models.CharField("Название", max_length=200)
    color = models.CharField(
        "Цвет", max_length=7, help_text="Цвет должен быть в 16х формате"
    )
    slug = models.SlugField("Slug", max_length=200)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        "recipes.Recipe",
        verbose_name="Ингредиенты",
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        "recipes.Ingredient",
        on_delete=models.CASCADE,
        verbose_name="Рецепты",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=(MinValueValidator(MIN_AMOUNT),),
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return str(self.ingredient)


class Ingredient(models.Model):
    name = models.CharField(
        "Название", help_text="Введите название ингридиента", max_length=200
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        help_text="Введите единицу измерения",
        max_length=200,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        "Название", help_text="Введите название рецепта", max_length=200
    )
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
        help_text="Автор рецепта",
    )
    image = models.ImageField(
        "Картинка",
        upload_to="recipes/",
        blank=True,
        help_text="Загрузите изображение",
    )
    text = models.TextField("Описание", help_text="Введите описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        through=IngredientInRecipe,
        through_fields=("recipe", "ingredient"),
        verbose_name="Ингредиенты",
        help_text="Выберите ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag, verbose_name="Теги", help_text="Выберите теги"
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=(MinValueValidator(MIN_COOK_TIME),),
        help_text="В минутах",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


@receiver(post_delete, sender=Recipe)
def handle_recipe_post_delete(instance, **kwargs):
    try:
        os.remove(instance.image.path)
    except FileNotFoundError:
        pass


class RecipeInCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Список покупок",
        help_text="Список покупок пользователя",
        related_name="purchases",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="В списке у пользователей",
        related_name="cart_recipe",
    )

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзинах"
        constraints = (
            models.UniqueConstraint(
                name="unique_cart_item",
                fields=("user", "recipe"),
            ),
        )


class RecipeInFavorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Избранные рецепты",
        help_text="Избранные рецепты пользователя",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Избранные у пользователей",
        help_text="Избранные рецепты у пользователей",
        related_name="favorite_recipe",
    )

    class Meta:
        verbose_name = "Рецепт в избранном"
        verbose_name_plural = "Рецепты в избранном"
        constraints = (
            models.UniqueConstraint(
                name="unique_favorite",
                fields=("user", "recipe"),
            ),
        )


class Follow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="подписчик",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                name="unique_follow",
                fields=("user", "author"),
            ),
            models.CheckConstraint(
                name="prevent_self_follow",
                check=~models.Q(user=models.F("author")),
            ),
        )

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
