# from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from recipes.models import Follow, Recipe, Tag
from recipes.serializers import (
    FollowSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSerializer,
)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from rest_framework.permissions import IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


User = get_user_model()


class FollowViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    @action(detail=False)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        # serializer = UserSerializer(page, many=True)
        # return self.get_paginated_response(serializer.data)
        page_query_param = "page"
        # page_size = request.GET[r"page_size"]
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginator.page_query_param = page_query_param
        # qry_set = Data.objects.all()
        p = paginator.paginate_queryset(
            queryset=queryset, request=request
        )  # change 1
        serializer = UserSerializer(p, many=True)  # change 2
        theData = serializer.data
        return paginator.get_paginated_response(theData)  # change 3

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


class FollowersViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("following__username",)

    def get_queryset(self):
        user = self.request.user
        return user.following.all()
