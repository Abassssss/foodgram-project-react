from django.contrib import admin
from django.utils.html import format_html
from recipes.models import Follow, Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "get_color", "slug")

    @admin.display(description="color")
    def get_color(self, tag):
        return format_html(
            '<div><span style="{}"></span>{}</div>',
            f"background-color:{tag.color};display:inline-block;width:20px;height:12px;border-radius:3px;margin:0 5px;",
            tag.color,
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit", "id")  # 5️⃣


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ("__str__", "recipe", "ingredient", "id")


admin.site.register(Follow)
