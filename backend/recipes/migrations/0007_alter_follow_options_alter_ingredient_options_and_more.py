# Generated by Django 4.0.5 on 2022-07-08 07:54

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0006_remove_recipe_cooking_time_recipe_cooking_time'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientinrecipe',
            options={'verbose_name': 'Ингредиент в рецепте', 'verbose_name_plural': 'Ингредиенты в рецептах'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipeincart',
            options={'verbose_name': 'Рецепт в корзине', 'verbose_name_plural': 'Рецепты в корзинах'},
        ),
        migrations.AlterModelOptions(
            name='recipeinfavorite',
            options={'verbose_name': 'Рецепт в избранном', 'verbose_name_plural': 'Рецепты в избранном'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Тэг', 'verbose_name_plural': 'Тэги'},
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(help_text='Введите единицу измерения', max_length=200, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient', verbose_name='Рецепты'),
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(help_text='В минутах', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите изображение', upload_to='recipes/', verbose_name='Картинка'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Выберите ингредиенты', through='recipes.IngredientInRecipe', to='recipes.ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите теги', to='recipes.tag', verbose_name='Теги'),
        ),
        migrations.AlterField(
            model_name='recipeincart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_recipe', to='recipes.recipe', verbose_name='В списке у пользователей'),
        ),
        migrations.AlterField(
            model_name='recipeincart',
            name='user',
            field=models.ForeignKey(help_text='Список покупок пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to=settings.AUTH_USER_MODEL, verbose_name='Список покупок'),
        ),
        migrations.AlterField(
            model_name='recipeinfavorite',
            name='recipe',
            field=models.ForeignKey(help_text='Избранные рецепты у пользователей', on_delete=django.db.models.deletion.CASCADE, related_name='favorite_recipe', to='recipes.recipe', verbose_name='Избранные у пользователей'),
        ),
        migrations.AlterField(
            model_name='recipeinfavorite',
            name='user',
            field=models.ForeignKey(help_text='Избранные рецепты пользователя', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Избранные рецепты'),
        ),
        migrations.AddConstraint(
            model_name='ingredientinrecipe',
            constraint=models.CheckConstraint(check=models.Q(('amount__gte', 1)), name='amount'),
        ),
        migrations.AddConstraint(
            model_name='recipeincart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_cart_item'),
        ),
    ]