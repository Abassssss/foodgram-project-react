import django_filters as filters

from .models import Ingredient, Recipe


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    ...


class RecipeFilter(filters.FilterSet):
    tags = CharInFilter(field_name="tags__slug", lookup_expr="in")

    class Meta:
        model = Recipe
        fields = ("tags",)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)
