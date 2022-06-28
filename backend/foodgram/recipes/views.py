from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Follow, Ingredient, Recipe, Tag
from recipes.serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSerializer,
)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter

# from rest_framework.permissions import IsAuthenticated
# 😢 😀 💯


class MyPageNumberPagination(PageNumberPagination):
    page_size_query_param = "limit"


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = MyPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if (
            self.action == "create"
            or self.action == "partial_update"
            or self.action == "update"
        ):
            return RecipeCreateSerializer
        else:
            return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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
    # pagination_class = LimitOffsetPagination


# class FavoriteViewSet(viewsets.ModelViewSet):
#     queryset =
#     serializer_class =
