# from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Recipe, Tag
from recipes.serializers import RecipeSerializer, TagSerializer
from rest_framework import filters, mixins, viewsets
from rest_framework.pagination import LimitOffsetPagination

# from rest_framework.permissions import IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
