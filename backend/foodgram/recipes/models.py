from django.conf import settings
from django.db import models
from django.db.models.deletion import SET_NULL


class Tag(models.Model):
    title = models.CharField("Название", max_length=20)
    hex_code = models.CharField("hex_code", max_length=9)
    slug = models.SlugField("slug")


class IngredientAmount(models.TextChoices):
    JAR = "банка"
    LOAF = "батон"
    BOTTLE = "бутылка"
    BRANCH = "веточка"
    GR = "г"
    HANDFUL = "горсть"
    SLICE = "долька"
    STAR = "звездочка"
    ZUB4IK = "зубчик"
    DROP = "капля"
    KG = "кг"
    CHUNK = "кусок"
    LITER = "л"
    LEAF = "лист"
    ML = "мл"
    BAG = "пакет"
    BAG2 = "пакетик"
    PACKET = "пачка"
    LAYER = "пласт"
    BYTASTE = "по вкусу"
    PU4OK = "пучок"
    TABLE_SPOON = "ст. л."
    GLASS = "стакан"
    STEM = "стебель"
    POD = "стручок"
    CARCASS = "тушка"
    PACKAGE = "упаковка"
    TEA_SPOON = "ч. л."
    PIECE = "шт."
    PINCH = "щепотка"


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey("recipes.Recipe", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        "recipes.Ingredient", on_delete=models.CASCADE
    )
    amount = models.IntegerField("Колличество")


class Ingredient(models.Model):
    title = models.CharField(
        "Название", help_text="Введите название ингридиента", max_length=50
    )
    unit = models.CharField(
        "Единица измерения",
        help_text="Введите единицу измерения",
        choices=IngredientAmount.choices,
        max_length=15,
    )


class Recipe(models.Model):
    title = models.CharField(
        "Название", help_text="Введите название рецепта", max_length=50
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
    description = models.TextField(
        "Описание", help_text="Введите описание рецепта"
    )
    ingridients = models.ManyToManyField(
        Ingredient, through=IngredientInRecipe
    )
    tag = models.ForeignKey(
        Tag,
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name="recipes",
        verbose_name="Тэг",
        help_text="Выберите тэг",
    )
    cook_time = models.IntegerField("Время приготовления")

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.title
