from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Tag(models.Model):
    name = models.CharField("Название", max_length=200)
    color = models.CharField(
        "Цвет", max_length=7, help_text="Цвет должен быть в 16х формате"
    )
    slug = models.SlugField("Slug", max_length=200)

    def __str__(self):
        return self.name


class IngredientAmount(models.TextChoices):
    JAR = ("банка", "банка")
    LOAF = ("батон", "батон")
    BOTTLE = ("бутылка", "бутылка")
    BRANCH = ("веточка", "веточка")
    GR = ("г", "г")
    HANDFUL = ("горсть", "горсть")
    SLICE = ("долька", "долька")
    STAR = ("звездочка", "звездочка")
    ZUB4IK = ("зубчик", "зубчик")
    DROP = ("капля", "капля")
    KG = ("кг", "кг")
    CHUNK = ("кусок", "кусок")
    LITER = ("л", "л")
    LEAF = ("лист", "лист")
    ML = ("мл", "мл")
    BAG = ("пакет", "пакет")
    BAG2 = ("пакетик", "пакетик")
    PACKET = ("пачка", "пачка")
    LAYER = ("пласт", "пласт")
    BYTASTE = ("по вкусу", "по вкусу")
    PU4OK = ("пучок", "пучок")
    TABLE_SPOON = ("ст. л.", "ст. л.")
    GLASS = ("стакан", "стакан")
    STEM = ("стебель", "стебель")
    POD = ("стручок", "стручок")
    CARCASS = ("тушка", "тушка")
    PACKAGE = ("упаковка", "упаковка")
    TEA_SPOON = ("ч. л.", "ч. л.")
    PIECE = ("шт.", "шт.")
    PINCH = ("щепотка", "щепотка")


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        "recipes.Ingredient", on_delete=models.CASCADE
    )
    amount = models.IntegerField("Количество")

    def __str__(self):
        return str(self.ingredient)


class Ingredient(models.Model):
    name = models.CharField(
        "Название", help_text="Введите название ингридиента", max_length=200
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        help_text="Введите единицу измерения",
        choices=IngredientAmount.choices,
        max_length=200,
    )

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
        help_text="Загрузите картинку",
    )
    text = models.TextField("Описание", help_text="Введите описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient, through=IngredientInRecipe
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэг",
    )
    cooking_time = models.PositiveIntegerField(
        "Время приготовления",
        validators=(MinValueValidator(1),),
        help_text="В минутах",
    )

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ("-pub_date",)

        constraints = (
            models.CheckConstraint(
                name="cooking_time",
                check=models.Q(name__gte=1),
            ),
        )

    def __str__(self):
        return self.name


class RecipeInCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="purchases",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="cart_recipe",
    )


class RecipeInFavorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="favorite_recipe",
    )

    class Meta:
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
