from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Follow, Ingredient, IngredientInRecipe, Recipe,
                            RecipeInCart, RecipeInFavorite, Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        write_only=True
    )  # TODO: add validator for min and max

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit", "amount")
        read_only_fields = ("name", "measurement_unit")

    def validate_id(self, id_):
        if not Ingredient.objects.filter(id=id_).exists():
            raise serializers.ValidationError(
                f'Ingredient with id "{id_}" does not exist.'
            )
        return id_


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )
        read_only_fields = ("name", "measurement_unit")


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_author(self, recipe):
        return UserSerializer(recipe.author, omit=("recipes",)).data

    def get_is_favorited(self, recipe):
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return None

        return RecipeInFavorite.objects.filter(
            user=request.user, recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return None

        return RecipeInCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        tags = TagSerializer(instance.tags.all(), many=True).data
        ingredients = IngredientInRecipeSerializer(
            instance.ingredientinrecipe_set.prefetch_related("ingredient"),
            many=True,
        ).data
        representation["tags"] = tags
        representation["ingredients"] = ingredients

        return representation

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")

        with transaction.atomic():
            recipe = super().create(validated_data)
            recipe.tags.set(tags)

            ingredients = []
            for ingredient in ingredients_data:
                ing = Ingredient.objects.get(id=ingredient["id"])
                ing_in_recipe = IngredientInRecipe(
                    recipe=recipe, ingredient=ing, amount=ingredient["amount"]
                )
                ingredients.append(ing_in_recipe)

            IngredientInRecipe.objects.bulk_create(ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients_data = validated_data.pop("ingredients")

        with transaction.atomic():
            instance = super().update(instance, validated_data)
            instance.tags.set(tags)

            IngredientInRecipe.objects.filter(recipe=instance).delete()

            ingredients = []
            for ingredient in ingredients_data:
                ingredients.append(
                    IngredientInRecipe(
                        recipe=instance,
                        ingredient=Ingredient.objects.get(id=ingredient["id"]),
                        amount=ingredient["amount"],
                    )
                )

            IngredientInRecipe.objects.bulk_create(ingredients)

        return instance


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    def validate(self, data):
        request = self.context.get("request")

        if request is None:
            return data

        user = request.user
        following = data["following"]

        if user == following:
            raise serializers.ValidationError("Нельзя подписаться на себя")

        return data

    class Meta:
        model = Follow
        fields = ("__all__",)
        validators = (
            UniqueTogetherValidator(
                queryset=Follow.objects.all(), fields=("user", "following")
            ),
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("first_name", "last_name", "email", "username", "password")


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        ref_name = "ReadOnlyUsers"

    def __init__(self, *args, **kwargs):
        omit = kwargs.pop("omit", [])
        super().__init__(*args, **kwargs)
        for field in omit:
            del self.fields[field]

    def get_recipes(self, user):
        request = self.context.get("request")
        queryset = user.recipes.all()

        if request is not None:
            recipes_limit = request.query_params.get("recipes_limit")
            if recipes_limit is not None:
                try:
                    recipes_limit_int = int(recipes_limit)
                except ValueError:
                    pass
                else:
                    queryset = queryset[:recipes_limit_int]

        return RecipeSerializer(queryset, many=True, context=self.context).data

    def get_recipes_count(self, user):
        return user.recipes.count()

    def get_is_subscribed(self, user):
        request = self.context.get("request")

        if request is None or request.user.is_anonymous:
            return None

        return Follow.objects.filter(user=request.user, author=user).exists()
