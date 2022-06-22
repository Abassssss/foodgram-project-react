from django.contrib import admin
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline,)


admin.site.register(Ingredient)
admin.site.register(IngredientInRecipe)
admin.site.register(Tag)
