from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = routers.DefaultRouter()
router.register("recipes", RecipeViewSet)
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
# router.register("groups", GroupViewSet)
# router.register("follow", FollowViewSet, basename="follow")
# router.register("followers", FollowersViewSet, basename="followers")

# comments_router = routers.DefaultRouter()
# comments_router.register("comments", CommentViewSet, basename="comment")


urlpatterns = [
    path("", include(router.urls)),
    # path("v1/posts/<int:post_id>/", include(comments_router.urls)),
]
