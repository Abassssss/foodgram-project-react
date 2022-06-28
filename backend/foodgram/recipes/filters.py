import django_filters as filters

from .models import Recipe


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    ...


# 🤛 🦉
class RecipeFilter(filters.FilterSet):
    # tags = filters.AllValuesMultipleFilter(field_name="tags__slug")
    tags = CharInFilter(field_name="tags__slug", lookup_expr="in")

    class Meta:
        model = Recipe
        fields = ("tags",)
