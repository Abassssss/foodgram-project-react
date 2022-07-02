from datetime import datetime

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (
    Follow,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    RecipeInCart,
    RecipeInFavorite,
    Tag,
)
from recipes.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSerializer,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter


class MyPageNumberPagination(PageNumberPagination):
    page_size_query_param = "limit"


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = MyPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        # if self.action in ("create", "update", "partial_update"):
        #     return RecipeCreateSerializer # NEEDS A COMMENT
        # else:
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["POST"])
    def favorite(self, request, **kwargs):
        user = request.user
        recipe = self.get_object()
        _, is_created = RecipeInFavorite.objects.get_or_create(
            user=user, recipe=recipe
        )

        if not is_created:
            data = {"message": "You have already liked this recipe"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, **kwargs):
        user = request.user
        recipe = self.get_object()
        count, _ = RecipeInFavorite.objects.filter(
            user=user, recipe=recipe
        ).delete()

        if count == 0:
            data = {"message": "No active favorite found."}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"])
    def shopping_cart(self, request, **kwargs):
        user = request.user
        recipe = self.get_object()
        _, is_created = RecipeInCart.objects.get_or_create(
            user=user, recipe=recipe
        )

        if not is_created:
            data = {"message": "This recipe already added"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def uncart(self, request, **kwargs):
        user = request.user
        recipe = self.get_object()
        count, _ = RecipeInCart.objects.filter(
            user=user, recipe=recipe
        ).delete()

        if count == 0:
            data = {"message": "No recipe found."}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def download_shopping_cart(self, request):
        shopping_cart = request.user.purchases.all()
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in=[cart_item.recipe for cart_item in shopping_cart]
        ).select_related("ingredient")

        shopping_dict = {}
        for cart_item in shopping_cart:
            recipe = cart_item.recipe
            recipe_ingredients = [
                ing for ing in ingredients if ing.recipe == recipe
            ]
            for ingredient in recipe_ingredients:
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                if name not in shopping_dict:
                    shopping_dict[name] = {
                        "amount": 0,
                        "measurement_unit": measurement_unit,
                    }
                shopping_dict[name]["amount"] += ingredient.amount
        shopping_list = []
        for i, item in enumerate(shopping_dict):
            shopping_list.append(
                f"{i + 1}. {item} - {shopping_dict[item]['amount']}{shopping_dict[item]['measurement_unit']}\n"
            )
        shopping_list.append(f"\nfoodgram, {datetime.now().year}")
        response = HttpResponse(shopping_list)
        response["Content-Type"] = "text/plain"
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_list.txt"'
        return response


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


User = get_user_model()


class FollowViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    @action(detail=False)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_size_query_param = "limit"

        page = paginator.paginate_queryset(queryset=queryset, request=request)
        serializer = self.get_serializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=["POST"])
    def subscribe(self, request, **kwargs):
        user = request.user
        author = self.get_object()
        _, is_created = Follow.objects.get_or_create(user=user, author=author)

        if not is_created:
            data = {"message": "You are already subscribed."}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        user = request.user
        author = self.get_object()
        count, _ = Follow.objects.filter(user=user, author=author).delete()

        if count == 0:
            data = {"message": "No active subscription found."}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
