from django.contrib import admin
from django.utils.html import format_html

from recipes.models import (Follow, Ingredient, IngredientInRecipe, Recipe,
                            RecipeInCart, RecipeInFavorite, Tag)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline,)
    search_fields = (
        "name",
        "author__first_name",
        "author__last_name",
        "author__username",
        "author__email",
        "tags__name",
    )
    list_display = ("__str__", "get_favorites")
    list_filter = ("tags__name",)

    @admin.display(description="Добавили в избранное")
    def get_favorites(self, recipe):
        return recipe.favorite_recipe.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "get_color", "slug")

    @admin.display(description="цвет")
    def get_color(self, tag):
        return format_html(
            '<div><span style="{}"></span>{}</div>',
            (
                f"background-color:{tag.color};display:inline-block;width:20px"
                ";height:12px;border-radius:3px;margin:0 5px;"
            ),
            tag.color,
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit", "id")
    list_filter = ("measurement_unit",)
    search_fields = ("name",)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ("__str__", "recipe", "ingredient", "id")
    list_filter = ("recipe__tags__name",)
    search_fields = (
        "recipe__name",
        "ingredient__name",
        "recipe__author__username",
        "recipe__author__email",
    )


@admin.register(RecipeInCart)
class RecipeInCartAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "recipe")
    search_fields = (
        "recipe__name",
        "recipe__author__username",
        "recipe__author__email",
    )


@admin.register(RecipeInFavorite)
class RecipeInFavoriteAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "recipe")
    search_fields = (
        "recipe__name",
        "recipe__author__username",
        "recipe__author__email",
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user", "author")
    search_fields = (
        "user__username",
        "user__email",
        "author__username",
        "author__email",
    )
