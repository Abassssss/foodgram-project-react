from django.urls import include, path
from rest_framework import routers

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet

router = routers.DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
urlpatterns = [
    path("", include(router.urls)),
]
